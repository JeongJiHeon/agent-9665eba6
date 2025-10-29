"""
LangChain-based Google Calendar Agent.
"""
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from typing import List, Dict, Any, Optional
from loguru import logger

from ..config import settings
from .tools import (
    CreateCalendarEventTool,
    ListCalendarEventsTool,
    UpdateCalendarEventTool,
    DeleteCalendarEventTool,
    ParseNaturalLanguageDateTool,
)


class CalendarAgent:
    """Google Calendar AI Agent using LangChain."""
    
    def __init__(self, calendar_service, user_id: str):
        """
        Initialize the calendar agent.
        
        Args:
            calendar_service: Google Calendar service instance
            user_id: User identifier for managing conversation memory
        """
        self.calendar_service = calendar_service
        self.user_id = user_id
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.memory = self._initialize_memory()
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=settings.DEBUG,
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            handle_parsing_errors=True,
        )
        
        logger.info(f"Initialized CalendarAgent for user {user_id}")
    
    def _initialize_llm(self):
        """Initialize the language model."""
        if settings.LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY,
            )
        elif settings.LLM_PROVIDER == "anthropic":
            return ChatAnthropic(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                api_key=settings.ANTHROPIC_API_KEY,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
    
    def _initialize_tools(self) -> List:
        """Initialize agent tools."""
        return [
            CreateCalendarEventTool(self.calendar_service),
            ListCalendarEventsTool(self.calendar_service),
            UpdateCalendarEventTool(self.calendar_service),
            DeleteCalendarEventTool(self.calendar_service),
            ParseNaturalLanguageDateTool(),
        ]
    
    def _initialize_memory(self) -> ConversationBufferMemory:
        """Initialize conversation memory."""
        return ConversationBufferMemory(
            memory_key=settings.CONVERSATION_MEMORY_KEY,
            return_messages=True,
            max_token_limit=settings.AGENT_MEMORY_SIZE * 100,
        )
    
    def _create_agent(self):
        """Create the LangChain agent."""
        system_prompt = """당신은 구글 캘린더를 관리하는 AI 어시스턴트입니다.

당신의 역할:
1. 사용자가 자연어로 입력한 일정을 이해하고 구글 캘린더에 이벤트를 생성합니다.
2. 기존 일정을 조회, 수정, 삭제할 수 있습니다.
3. 날짜와 시간을 정확하게 파싱하여 ISO 8601 형식으로 변환합니다.
4. 친절하고 정확한 응답을 제공합니다.

지침:
- 사용자가 일정을 추가하려고 할 때, 제목, 시작 시간, 종료 시간을 명확히 파악하세요.
- 시간이 명시되지 않은 경우, 사용자에게 물어보세요.
- 날짜 파싱이 필요한 경우 parse_date 도구를 사용하세요.
- 일정 생성 후 확인 메시지를 제공하세요.
- 오류 발생 시 사용자에게 명확하게 설명하세요.

현재 시간 정보를 고려하여 날짜를 정확하게 파싱하세요.
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name=settings.CONVERSATION_MEMORY_KEY),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        return create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process user message and return agent response.
        
        Args:
            message: User input message
            
        Returns:
            Dict containing response and metadata
        """
        try:
            logger.info(f"Processing message for user {self.user_id}: {message}")
            
            result = await self.agent_executor.ainvoke({"input": message})
            
            response = {
                "success": True,
                "message": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
            }
            
            logger.info(f"Agent response: {response['message']}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}",
                "error": str(e),
            }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        messages = self.memory.chat_memory.messages
        return [
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content,
            }
            for msg in messages
        ]
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.memory.clear()
        logger.info(f"Cleared conversation history for user {self.user_id}")


class AgentManager:
    """Manage multiple agent instances for different users."""
    
    def __init__(self):
        self.agents: Dict[str, CalendarAgent] = {}
    
    def get_agent(self, user_id: str, calendar_service) -> CalendarAgent:
        """Get or create agent for user."""
        if user_id not in self.agents:
            self.agents[user_id] = CalendarAgent(calendar_service, user_id)
        return self.agents[user_id]
    
    def remove_agent(self, user_id: str):
        """Remove agent for user."""
        if user_id in self.agents:
            del self.agents[user_id]


# Global agent manager instance
agent_manager = AgentManager()
