"""
The Third Voice AI - FastAPI Main Application
Entry point for the FastAPI backend with all routes and middleware
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import traceback

# Import your modules
from src.core.config import settings
from src.data.database import db_manager, get_database_manager
from src.auth.auth_manager import auth_manager, get_current_user, get_current_user_optional
from src.ai.ai_engine import ai_engine
from src.data.peewee_models import create_tables
from src.api.routes import auth, contacts, messages, feedback, health
from src.core.exceptions import AppException, ValidationException
from src.core.custom_logging import setup_logging
from src.data.schemas import HealthCheck, ErrorResponse

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting The Third Voice AI Backend")

    try:
        # Initialize database
        create_tables()
        logger.info("✅ Database initialized")

        # Setup auth manager with database
        auth_manager.db = db_manager
        logger.info("✅ Authentication manager configured")

        # AI engine is already initialized
        logger.info("✅ AI engine ready")

        # Background tasks could go here
        logger.info("🎭 The Third Voice AI Backend is ready!")

        yield

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    finally:
        # Shutdown
        logger.info("🔄 Shutting down The Third Voice AI Backend")
        try:
            await ai_engine.cleanup()
            logger.info("✅ AI engine cleaned up")
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {e}")

# Create FastAPI application
app = FastAPI(
    title="The Third Voice AI",
    description="AI-powered communication assistant for difficult conversations - Healing families through better communication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # Changed from settings.ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (for production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Global exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_type,
            detail=exc.message,
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions"""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="validation_error",
            detail=exc.message,
            errors=exc.errors,
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")

    if settings.ENVIRONMENT == "development":
        detail = str(exc)
    else:
        detail = "An unexpected error occurred"

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            detail=detail,
            timestamp=datetime.now()
        ).dict()
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])

# Root endpoint - Concise but meaningful Third Voice message
@app.get("/", response_model=Dict[str, Any])
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with The Third Voice AI information"""
    return {
        "welcome": "💙 The Third Voice AI - Healing families through better communication",
        "mission": "When two hearts struggle to connect, we become the voice of compassion",
        "born_from": "Built with love during 15 months in detention, for Samantha and all families",
        "philosophy": "It's not just a chatbot. It's the voice of compassion when the other person can't hear you.",
        "breakthrough": "August 20, 2025: First transformation achieved 8/10 healing score",
        "dedication": "For Samantha. For All. 💙",
        "version": "1.0.0",
        "status": "ready to heal conversations",
        "contexts": ["romantic", "coparenting", "family", "workplace", "friends"],
        "docs": "/docs",
        "health": "/api/health",
        "demo": "/api/auth/demo",
        "timestamp": datetime.now()
    }

# Health check endpoint (duplicate for convenience)
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Quick health check endpoint"""
    try:
        db_health = await db_manager.health_check()

        return HealthCheck(
            status="healthy",
            database=db_health.get("database", False),
            ai_engine=True,  # ai_engine is always initialized
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=0.0,  # Could implement actual uptime tracking
            demo_users_active=len(db_manager._demo_contacts)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            database=False,
            ai_engine=False,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=0.0
        )

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        reload_dirs=["src"] if settings.ENVIRONMENT == "development" else None
    )