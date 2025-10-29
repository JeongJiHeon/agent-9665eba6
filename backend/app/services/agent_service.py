"""
Agent service for managing conversations.
"""
from typing import Dict, Any, List
from loguru import logger

from ..agents.calendar_agent import agent_manager
from .calendar_service import calendar_service_manager


class AgentService:
    """Service for managing agent interactions."""
    
    @staticmethod
    async def process_user_message(
        user_id: str,
        message: str,
        credentials: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user message through the agent.
        
        Args:
            user_id: User identifier
            message: User message
            credentials: Google OAuth credentials
            
        Returns:
            Agent response
        """
        try:
            # Get or create calendar service
            calendar_service = calendar_service_manager.get_service(user_id, credentials)
            
            # Check authentication
            if not calendar_service.is_authenticated():
                return {
                    "success": False,
                    "message": "구글 캘린더 인증이 필요합니다. 먼저 인증을 진행해주세요.",
                    "requires_auth": True,
                }
            
            # Get or create agent
            agent = agent_manager.get_agent(user_id, calendar_service)
            
            # Process message
            response = await agent.process_message(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in agent service: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"처리 중 오류가 발생했습니다: {str(e)}",
                "error": str(e),
            }
    
    @staticmethod
    def get_conversation_history(user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for user."""
        try:
            agent = agent_manager.agents.get(user_id)
            if agent:
                return agent.get_conversation_history()
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    @staticmethod
    def clear_conversation_history(user_id: str):
        """Clear conversation history for user."""
        try:
            agent = agent_manager.agents.get(user_id)
            if agent:
                agent.clear_conversation_history()
            logger.info(f"Cleared conversation for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            raise
