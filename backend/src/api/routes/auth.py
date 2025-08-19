"""
Authentication API routes for The Third Voice AI
JWT-based authentication with demo user support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any
import logging

from ...auth.auth_manager import (
    auth_manager, 
    get_current_user, 
    get_current_user_optional,
    TokenResponse,
    LoginRequest, 
    DemoResponse,
    RefreshTokenRequest
)
from ...data.schemas import UserCreate, UserResponse, ErrorResponse
from ...core.exceptions import (
    AuthenticationException,
    ValidationException,
    ConflictException
)

# Setup
router = APIRouter()
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: LoginRequest
) -> TokenResponse:
    """
    Login with email and password
    
    Supports both regular users and demo user:
    - Demo user: demo@thethirdvoice.ai / demo123
    - Regular users: Any registered email/password
    """
    try:
        logger.info(f"Login attempt for: {login_data.email}")
        
        # Validate email format
        if "@" not in login_data.email:
            raise ValidationException("Invalid email format")
        
        # Attempt authentication
        token_response = await auth_manager.login_user(login_data)
        
        logger.info(f"✅ Login successful for: {login_data.email}")
        return token_response
        
    except HTTPException:
        logger.warning(f"❌ Login failed for: {login_data.email}")
        raise
    except Exception as e:
        logger.error(f"❌ Login error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post("/demo", response_model=DemoResponse)
@limiter.limit("5/minute")
async def start_demo(request: Request) -> DemoResponse:
    """
    Start instant demo session
    
    Creates a temporary demo account with:
    - Pre-filled demo contact
    - 24-hour session token
    - Limited functionality showcase
    """
    try:
        logger.info("🎭 Starting demo session")
        
        demo_response = await auth_manager.start_demo_session()
        
        logger.info("✅ Demo session created successfully")
        return demo_response
        
    except Exception as e:
        logger.error(f"❌ Demo session creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create demo session"
        )


@router.post("/register", response_model=Dict[str, str])
@limiter.limit("5/minute") 
async def register(
    request: Request,
    user_data: UserCreate
) -> Dict[str, str]:
    """
    Register a new user account
    
    Creates a new user with:
    - Email validation
    - Password hashing
    - Account verification (future feature)
    """
    try:
        logger.info(f"Registration attempt for: {user_data.email}")
        
        # Validate password strength
        if len(user_data.password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        # Register user
        success, message, user = await auth_manager.register_new_user(user_data)
        
        if success:
            logger.info(f"✅ Registration successful for: {user_data.email}")
            return {
                "message": message,
                "email": user_data.email,
                "status": "success"
            }
        else:
            logger.warning(f"❌ Registration failed for {user_data.email}: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except ValidationException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest
) -> TokenResponse:
    """
    Refresh an existing JWT token
    
    Extends token expiry without requiring re-login
    """
    try:
        logger.info("🔄 Token refresh attempt")
        
        new_token = await auth_manager.refresh_token(refresh_data.refresh_token)
        
        if not new_token:
            logger.warning("❌ Token refresh failed - invalid token")
            raise AuthenticationException("Invalid refresh token")
        
        # For demo tokens, return demo response format
        payload = auth_manager.decode_token(new_token)
        is_demo = payload.get("is_demo", False)
        
        if is_demo:
            demo_user = UserResponse(
                id=auth_manager.DEMO_USER["id"],
                email=auth_manager.DEMO_USER["email"],
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return TokenResponse(
                access_token=new_token,
                expires_in=int(timedelta(hours=auth_manager.DEMO_TOKEN_EXPIRE_HOURS).total_seconds()),
                user=demo_user
            )
        else:
            # Regular user - would need to fetch user data
            # For now, return minimal response
            return TokenResponse(
                access_token=new_token,
                expires_in=int(timedelta(minutes=auth_manager.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
                user=UserResponse(
                    id=payload["sub"],
                    email=payload.get("email", ""),
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
        
        logger.info("✅ Token refresh successful")
        
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
@limiter.limit("10/minute")
async def logout(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Logout current user
    
    Invalidates the current session
    """
    try:
        logger.info(f"Logout for user: {current_user.email}")
        
        await auth_manager.logout_user(current_user)
        
        return {
            "message": "Logged out successfully",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
@limiter.limit("30/minute")
async def get_current_user_info(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information
    
    Returns user profile and account status
    """
    logger.info(f"Profile request for: {current_user.email}")
    return current_user


@router.get("/verify")
@limiter.limit("10/minute") 
async def verify_token(
    request: Request,
    current_user: UserResponse = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Verify if current token is valid
    
    Useful for frontend to check authentication status
    """
    if current_user:
        is_demo = auth_manager.is_demo_user(current_user)
        
        return {
            "valid": True,
            "user": current_user,
            "is_demo": is_demo,
            "expires_soon": False  # Could implement expiry checking
        }
    else:
        return {
            "valid": False,
            "user": None,
            "is_demo": False,
            "expires_soon": False
        }


@router.get("/demo/stats")
@limiter.limit("20/minute")
async def get_demo_stats(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get demo user statistics
    
    Shows usage stats and upgrade prompts for demo users
    """
    if not auth_manager.is_demo_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for demo users"
        )
    
    try:
        stats = auth_manager.get_demo_stats(current_user)
        show_upgrade = auth_manager.should_show_upgrade_prompt(current_user)
        
        return {
            **stats,
            "show_upgrade_prompt": show_upgrade,
            "remaining_demo_time": "Unlimited for demo",  # Could implement time tracking
            "upgrade_benefits": [
                "Unlimited contacts and messages",
                "Data persistence across sessions", 
                "Priority AI processing",
                "Export conversation history",
                "Email support"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting demo stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch demo statistics"
        )


# Add missing imports
from datetime import datetime, timedelta"""
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
from src.core.logging_config import setup_logging
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
    description="AI-powered communication assistant for difficult conversations",
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
    allow_origins=settings.ALLOWED_ORIGINS,
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

# Root endpoint
@app.get("/", response_model=Dict[str, Any])
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "message": "Welcome to The Third Voice AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health",
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
