"""Main Calendar AI Agent"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, AsyncIterator
from uuid import uuid4

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import HumanMessage
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.services.google_calendar import GoogleCalendarService
from app.agent.tools import get_calendar_tools
from app.agent.prompts import get_agent_prompt
from app.agent.memory import DatabaseChatMemory


class CalendarAgent:
    """LangChain-based calendar AI agent"""
    
    def __init__(self, db: Session, user: User, session_id: Optional[str] = None):
        """Initialize the calendar agent"""
        self.db = db
        self.user = user
        self.session_id = session_id or str(uuid4())
        
        # Initialize Google Calendar service
        self.calendar_service = GoogleCalendarService(user)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            streaming=True,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize memory
        self.memory = DatabaseChatMemory(
            db=db,
            user=user,
            session_id=self.session_id
        )
        
        # Initialize tools
        self.tools = get_calendar_tools(self.calendar_service)
        
        # Initialize agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor"""
        prompt = get_agent_prompt()
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        return agent_executor
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process a user message and return response"""
        try:
            # Load conversation history
            memory_vars = self.memory.load_memory_variables()
            
            # Prepare input with context
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            inputs = {
                "input": message,
                "current_time": current_time,
                "current_date": current_date,
                "chat_history": memory_vars.get("chat_history", [])
            }
            
            # Run agent
            result = self.agent.invoke(inputs)
            
            # Save conversation to database
            self.memory.save_context(
                {"input": message},
                {"output": result["output"]}
            )
            
            # Check if calendar event was created
            calendar_event_created = False
            event_details = None
            
            for step in result.get("intermediate_steps", []):
                action, observation = step
                if action.tool == "create_calendar_event":
                    calendar_event_created = True
                    event_details = action.tool_input
                    break
            
            return {
                "message": result["output"],
                "session_id": self.session_id,
                "calendar_event_created": calendar_event_created,
                "event_details": event_details,
                "metadata": {
                    "intermediate_steps": len(result.get("intermediate_steps", [])),
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        except Exception as e:
            return {
                "message": f"죄송합니다. 오류가 발생했습니다: {str(e)}",
                "session_id": self.session_id,
                "calendar_event_created": False,
                "event_details": None,
                "metadata": {"error": str(e)}
            }
    
    async def process_message_stream(self, message: str) -> AsyncIterator[str]:
        """Process message with streaming response"""
        try:
            # Load conversation history
            memory_vars = self.memory.load_memory_variables()
            
            # Prepare input
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            inputs = {
                "input": message,
                "current_time": current_time,
                "current_date": current_date,
                "chat_history": memory_vars.get("chat_history", [])
            }
            
            # Stream agent response
            async for chunk in self.agent.astream(inputs):
                if "output" in chunk:
                    yield chunk["output"]
            
            # Note: Memory is saved after streaming completes
            # This would need to be handled separately in production
        
        except Exception as e:
            yield f"오류: {str(e)}"
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.memory.clear()
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        memory_vars = self.memory.load_memory_variables()
        messages = memory_vars.get("chat_history", [])
        
        if not messages:
            return "대화 기록이 없습니다."
        
        summary = f"총 {len(messages)}개의 메시지\n\n"
        for i, msg in enumerate(messages[-5:], 1):  # Last 5 messages
            role = "사용자" if isinstance(msg, HumanMessage) else "AI"
            summary += f"{i}. [{role}] {msg.content[:100]}...\n"
        
        return summary
