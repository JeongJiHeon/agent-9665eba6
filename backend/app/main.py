"""FastAPI application main module."""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from contextlib import asynccontextmanager

from app.config import settings
from app.models import HealthCheck, ConversationRequest, ConversationResponse
from app.api.routes import router
from app.services.vector_store import vector_store_service

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)

# Add file logging
log_path = Path(settings.LOG_FILE)
log_path.parent.mkdir(parents=True, exist_ok=True)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Calendar Agent Application...")
    
    # Initialize services
    try:
        await vector_store_service.initialize()
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Calendar Agent Application...")


# Create FastAPI application
app = FastAPI(
    title="Google Calendar Agent API",
    description="AI-powered agent for managing Google Calendar with natural language",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")


@app.get("/", response_model=HealthCheck)
async def root():
    """Root endpoint - health check."""
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        services={
            "api": True,
            "vector_store": vector_store_service.is_initialized,
        }
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Detailed health check endpoint."""
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        services={
            "api": True,
            "vector_store": vector_store_service.is_initialized,
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1,
    )
