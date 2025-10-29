"""Main Calendar Agent implementation with LangChain."""

from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import AsyncCallbackHandler
from loguru import logger
import uuid

from app.config import settings
from app.agent.tools import get_calendar_tools
from app.agent.prompts import AGENT_PROMPT_TEMPLATE
from app.agent.memory import memory_manager


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Custom streaming callback handler."""
    
    def __init__(self):
        self.tokens = []
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token from LLM."""
        self.tokens.append(token)


class CalendarAgent:
    """
    Main Calendar Agent class that handles natural language calendar management.
    """
    
    def __init__(self):
        self.llm = None
        self.agent_executor: Optional[AgentExecutor] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the agent with LLM and tools."""
        if self._initialized:
            return
        
        try:
            # Initialize LLM based on provider
            if settings.LLM_PROVIDER == "openai":
                self.llm = ChatOpenAI(
                    model=settings.LLM_MODEL,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                    streaming=True,
                )
            elif settings.LLM_PROVIDER == "anthropic":
                self.llm = ChatAnthropic(
                    model=settings.LLM_MODEL,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                    streaming=True,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
            
            # Get tools
            tools = get_calendar_tools()
            
            # Create prompt with current date/time
            prompt = AGENT_PROMPT_TEMPLATE.partial(
                current_time=datetime.now().strftime("%H:%M:%S"),
                current_date=datetime.now().strftime("%Y-%m-%d (%A)"),
            )
            
            # Create agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt,
            )
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=settings.AGENT_VERBOSE,
                max_iterations=settings.AGENT_MAX_ITERATIONS,
                handle_parsing_errors=True,
                return_intermediate_steps=True,
            )
            
            self._initialized = True
            logger.info(f"Calendar agent initialized with {settings.LLM_PROVIDER}")
        
        except Exception as e:
            logger.error(f"Failed to initialize calendar agent: {e}")
            raise
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: str = "default_user",
    ) -> Dict[str, Any]:
        """
        Process a user message and return agent response.
        
        Args:
            message: User's natural language input
            session_id: Session identifier (creates new if None)
            user_id: User identifier
            
        Returns:
            Dictionary containing response and metadata
        """
        if not self._initialized:
            self.initialize()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Get conversation memory
            memory = memory_manager.get_memory(session_id)
            
            # Run agent
            result = await self.agent_executor.ainvoke(
                {
                    "input": message,
                    "chat_history": memory.chat_memory.messages,
                },
            )
            
            response = result["output"]
            
            # Save to memory
            await memory_manager.add_message(session_id, message, is_user=True)
            await memory_manager.add_message(session_id, response, is_user=False)
            
            # Extract created events from intermediate steps
            events_created = []
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if hasattr(step, "tool") and "create" in step.tool.lower():
                        events_created.append(step.tool_input)
            
            return {
                "response": response,
                "session_id": session_id,
                "events_created": events_created,
                "success": True,
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": f"죄송합니다. 오류가 발생했습니다: {str(e)}",
                "session_id": session_id,
                "events_created": [],
                "success": False,
                "error": str(e),
            }
    
    async def stream_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: str = "default_user",
    ) -> AsyncIterator[str]:
        """
        Process message with streaming response.
        
        Args:
            message: User's natural language input
            session_id: Session identifier
            user_id: User identifier
            
        Yields:
            Response tokens
        """
        if not self._initialized:
            self.initialize()
        
        if not session_id:
            session_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Get conversation memory
            memory = memory_manager.get_memory(session_id)
            
            # Create streaming callback
            streaming_handler = StreamingCallbackHandler()
            
            # Run agent with streaming
            result = await self.agent_executor.ainvoke(
                {
                    "input": message,
                    "chat_history": memory.chat_memory.messages,
                },
                config={"callbacks": [streaming_handler]},
            )
            
            # Yield tokens
            for token in streaming_handler.tokens:
                yield token
            
            # Save to memory
            response = result["output"]
            await memory_manager.add_message(session_id, message, is_user=True)
            await memory_manager.add_message(session_id, response, is_user=False)
        
        except Exception as e:
            logger.error(f"Error streaming message: {e}")
            yield f"\n\n❌ 오류: {str(e)}"


# Global agent instance
calendar_agent = CalendarAgent()
