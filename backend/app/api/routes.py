"""API routes for the application."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from loguru import logger

from app.models import (
    ConversationRequest,
    ConversationResponse,
    AuthCallbackRequest,
    SearchQuery,
)
from app.agent.calendar_agent import calendar_agent
from app.agent.memory import memory_manager
from app.services.google_calendar import calendar_service
from app.services.vector_store import vector_store_service

router = APIRouter()


@router.post("/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """
    Main chat endpoint for conversational AI.
    
    Process user message and return AI response with any created events.
    """
    try:
        logger.info(f"Processing chat message from user: {request.user_id}")
        
        # Process message through agent
        result = await calendar_agent.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id,
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
        
        return ConversationResponse(
            message=result["response"],
            session_id=result["session_id"],
            events_created=result.get("events_created", []),
            suggestions=[],
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ConversationRequest):
    """
    Streaming chat endpoint.
    
    Returns streaming response for real-time AI responses.
    """
    try:
        logger.info(f"Processing streaming chat from user: {request.user_id}")
        
        async def generate():
            async for token in calendar_agent.stream_message(
                message=request.message,
                session_id=request.session_id,
                user_id=request.user_id,
            ):
                yield token
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of messages in the conversation
    """
    try:
        messages = await memory_manager.get_history(session_id)
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.type,
                "content": msg.content,
            })
        
        return {
            "session_id": session_id,
            "messages": formatted_messages,
            "count": len(formatted_messages),
        }
    
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear conversation history for a session.
    
    Args:
        session_id: Session identifier
    """
    try:
        await memory_manager.clear_history(session_id)
        return {
            "success": True,
            "message": f"History cleared for session: {session_id}"
        }
    
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/google")
async def google_auth(redirect_uri: Optional[str] = Query(None)):
    """
    Get Google OAuth authorization URL.
    
    Args:
        redirect_uri: Optional custom redirect URI
        
    Returns:
        Authorization URL
    """
    try:
        if not redirect_uri:
            from app.config import settings
            redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        auth_url = calendar_service.get_authorization_url(redirect_uri)
        return {
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
        }
    
    except Exception as e:
        logger.error(f"Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/callback")
async def auth_callback(request: AuthCallbackRequest):
    """
    Handle Google OAuth callback.
    
    Args:
        request: Callback request with authorization code
        
    Returns:
        Success status
    """
    try:
        from app.config import settings
        
        success = await calendar_service.handle_oauth_callback(
            code=request.code,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="OAuth authentication failed")
        
        return {
            "success": True,
            "message": "Authentication successful"
        }
    
    except Exception as e:
        logger.error(f"Error in auth callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def list_events(
    query: Optional[str] = Query(None),
    max_results: int = Query(10, ge=1, le=100),
):
    """
    List calendar events.
    
    Args:
        query: Optional search query
        max_results: Maximum number of results
        
    Returns:
        List of events
    """
    try:
        events = await calendar_service.search_events(
            query=query,
            max_results=max_results,
        )
        
        return {
            "events": events,
            "count": len(events),
        }
    
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """
    Get a specific event by ID.
    
    Args:
        event_id: Event identifier
        
    Returns:
        Event details
    """
    try:
        event = await calendar_service.get_event(event_id)
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event.
    
    Args:
        event_id: Event identifier
        
    Returns:
        Success status
    """
    try:
        success = await calendar_service.delete_event(event_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Event not found or deletion failed")
        
        # Also delete from vector store
        await vector_store_service.delete_event(event_id)
        
        return {
            "success": True,
            "message": f"Event deleted: {event_id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_similar_events(request: SearchQuery):
    """
    Search for similar events using vector similarity (RAG).
    
    Args:
        request: Search query with parameters
        
    Returns:
        List of similar events
    """
    try:
        results = await vector_store_service.search_similar(
            query=request.query,
            top_k=request.top_k,
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
        }
    
    except Exception as e:
        logger.error(f"Error searching similar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-store/stats")
async def get_vector_store_stats():
    """
    Get vector store statistics.
    
    Returns:
        Collection statistics
    """
    try:
        stats = await vector_store_service.get_collection_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting vector store stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
