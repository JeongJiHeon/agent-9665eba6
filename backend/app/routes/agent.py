"""
Agent API routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger

from ..services.agent_service import AgentService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    success: bool
    message: str
    requires_auth: Optional[bool] = False
    error: Optional[str] = None


class ConversationHistoryResponse(BaseModel):
    """Conversation history response."""
    history: List[Dict[str, str]]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user message through the AI agent.
    
    Args:
        request: Chat request containing user message
        
    Returns:
        Agent response
    """
    try:
        # Use user_id from request or default to "demo_user"
        user_id = request.user_id or "demo_user"
        
        # Process message
        response = await AgentService.process_user_message(
            user_id=user_id,
            message=request.message
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str):
    """
    Get conversation history for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Conversation history
    """
    try:
        history = AgentService.get_conversation_history(user_id)
        return ConversationHistoryResponse(history=history)
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Success message
    """
    try:
        AgentService.clear_conversation_history(user_id)
        return {"message": "대화 기록이 삭제되었습니다."}
        
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
