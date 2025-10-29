"""AI Agent endpoints"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.deps import get_current_active_user
from app.schemas.conversation import AgentRequest, AgentResponse
from app.agent.calendar_agent import CalendarAgent

router = APIRouter()


@router.post("/chat", response_model=AgentResponse)
def chat_with_agent(
    request: AgentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Chat with the AI agent"""
    # Check if user has Google Calendar connected
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect your Google Calendar first"
        )
    
    try:
        # Initialize agent
        agent = CalendarAgent(
            db=db,
            user=current_user,
            session_id=request.session_id
        )
        
        # Process message
        response = agent.process_message(request.message)
        
        return AgentResponse(**response)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_with_agent_stream(
    request: AgentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StreamingResponse:
    """Chat with the AI agent (streaming response)"""
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect your Google Calendar first"
        )
    
    try:
        # Initialize agent
        agent = CalendarAgent(
            db=db,
            user=current_user,
            session_id=request.session_id
        )
        
        # Stream response
        async def generate():
            async for chunk in agent.process_message_stream(request.message):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
        )


@router.delete("/history/{session_id}")
def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Clear chat history for a session"""
    try:
        agent = CalendarAgent(
            db=db,
            user=current_user,
            session_id=session_id
        )
        
        agent.clear_history()
        
        return {"message": "Chat history cleared successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing history: {str(e)}"
        )


@router.get("/history/{session_id}/summary")
def get_conversation_summary(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get conversation summary"""
    try:
        agent = CalendarAgent(
            db=db,
            user=current_user,
            session_id=session_id
        )
        
        summary = agent.get_conversation_summary()
        
        return {"summary": summary}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting summary: {str(e)}"
        )
