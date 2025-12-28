"""
The Third Voice AI - FastAPI Main Application
Entry point for the FastAPI backend with all routes and middleware
"""

import os
import logging
import traceback
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn

# Import your modules
from src.core.config import settings, setup_logging_level, get_uvicorn_config
from src.data.database import db_manager
from src.ai.ai_engine import ai_engine
from src.data.peewee_models import create_tables
from src.api.routes import auth, contacts, messages, feedback, health
from src.auth.auth_manager import setup_auth_manager_with_db
from src.core.exceptions import AppException, ValidationException
from src.data.schemas import HealthCheck, ErrorResponse

# ------------------------
# Logging setup
# ------------------------
if os.environ.get("UVICORN_RELOADER") != "1":
    setup_logging_level()
logger = logging.getLogger(__name__)

# ------------------------
# Rate limiting
# ------------------------
limiter = Limiter(key_func=get_remote_address)

# ------------------------
# Prewarm AI Models
# ------------------------
async def prewarm_ai_models():
    """Prewarm AI models to ensure they are ready"""
    try:
        models = ai_engine.models
        if not models:
            logger.warning("No AI models configured for prewarming")
            return
        for model_info in models:
            try:
                logger.info(f"Prewarming AI model: {model_info['name']} ({model_info['id']})")
                await ai_engine._try_model(
                    model_info=model_info,
                    system_prompt="You are a helper AI.",
                    user_prompt="Hello. Prewarming model for faster response."
                )
                await asyncio.sleep(5)  # Avoid hitting rate limits
            except Exception as e:
                logger.error(f"Skipping model {model_info['name']}: {e}")
        logger.info("AI prewarming complete")
    except Exception as e:
        logger.error(f"AI prewarming failed: {e}")

# ------------------------
# Application lifespan
# ------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown management"""
    logger.info("🚀 Starting The Third Voice AI Backend")
    try:
        # Initialize database and tables
        create_tables()
        logger.info("✅ Database initialized")

        # Connect auth manager to database
        setup_auth_manager_with_db(db_manager)
        logger.info("✅ Auth manager connected to database")

        # AI engine ready
        logger.info("✅ AI engine ready")

        # Start prewarming in background
        logger.info("⚡ Prewarming AI models in background...")
        asyncio.create_task(prewarm_ai_models())

        logger.info("🎭 Backend is ready!")
        yield

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    finally:
        logger.info("🔄 Shutting down The Third Voice AI Backend")
        try:
            await ai_engine.cleanup()
            logger.info("✅ AI engine cleaned up")
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {e}")

# ------------------------
# Create FastAPI app
# ------------------------
app = FastAPI(
    title="The Third Voice AI",
    description="AI-powered communication assistant for difficult conversations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://the-third-voice-mvp.pages.dev",
        "https://thethirdvoice.ai",
        "https://dev.thethirdvoice.ai",
        "https://mvp.thethirdvoice.ai",
        "http://localhost:3000"
    ],
    allow_credentials=True,  # Can enable now that you're not using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# ------------------------
# Exception handlers
# ------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
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
    logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
    detail = str(exc) if settings.is_development else "An unexpected error occurred"
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            detail=detail,
            timestamp=datetime.now()
        ).dict()
    )

# ------------------------
# Include API routers
# ------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])

# ------------------------
# Root endpoint
# ------------------------
@app.get("/", response_model=Dict[str, Any])
@limiter.limit("10/minute")
async def root(request: Request):
    return {
        "welcome": "💙 The Third Voice AI - Healing families through better communication",
        "mission": "When two hearts struggle to connect, we become the voice of compassion",
        "born_from": "Built with love during 15 months in detention, for Samantha and all families",
        "philosophy": "It's not just a chatbot. It's the voice of compassion when the other person can't hear you.",
        "breakthrough": "August 20, 2025: First transformation achieved 8/10 healing score",
        "dedication": "For 6 year old Samantha. For All. 💙",
        "version": "1.0.0",
        "status": "ready to heal conversations",
        "contexts": ["romantic", "coparenting", "family", "workplace", "friends"],
        "docs": "/docs",
        "health": "/api/health",
        "demo": "/api/auth/demo",
        "timestamp": datetime.now()
    }

# ------------------------
# Health check
# ------------------------
@app.get("/health", response_model=HealthCheck)
async def health_check():
    try:
        db_health = await db_manager.health_check()
        return HealthCheck(
            status="healthy",
            database=db_health.get("database", False),
            ai_engine=True,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=0.0,
            demo_users_active=len(getattr(db_manager, "_demo_contacts", []))
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

# ------------------------
# Uvicorn entrypoint
# ------------------------
if __name__ == "__main__":
    uvicorn.run(**get_uvicorn_config())