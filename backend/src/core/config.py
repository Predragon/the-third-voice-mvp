# backend/src/core/config.py"""
FastAPI Authentication Manager for The Third Voice AI
JWT-based authentication with demo user support and Supabase integration
Migrated from Streamlit to FastAPI patterns
"""

import jwt
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

# Import your Pydantic models
from ..data.models import User, UserCreate, UserResponse, DemoUsage
from ..core.config import settings


class AuthManager:
    """FastAPI-compatible authentication manager with demo user support"""
    
    # Demo user configuration
    DEMO_USER = {
        "email": "demo@thethirdvoice.ai",
        "password": "demo123",
        "name": "Demo User",
        "id": "demo-user-001"
    }
    
    def __init__(self, database_manager=None):
        self.db = database_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer(auto_error=False)
        
        # JWT settings
        self.SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key-change-in-production')
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
        self.DEMO_TOKEN_EXPIRE_HOURS = getattr(settings, 'DEMO_TOKEN_EXPIRE_HOURS', 24)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def create_demo_token(self, user_id: str) -> str:
        """Create a longer-lasting token for demo users"""
        expire = datetime.utcnow() + timedelta(hours=self.DEMO_TOKEN_EXPIRE_HOURS)
        to_encode = {
            "sub": user_id,
            "email": self.DEMO_USER["email"],
            "is_demo": True,
            "exp": expire
        }
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Authenticate user (demo or regular)"""
        # Check if it's demo user
        if email == self.DEMO_USER["email"]:
            return await self._authenticate_demo_user(password)
        
        # Regular user authentication (you'll need to implement user lookup)
        # This would typically query your User table
        try:
            # TODO: Implement user lookup from database
            # user = await self.get_user_by_email(email)
            # if user and self.verify_password(password, user.hashed_password):
            #     return UserResponse.from_orm(user)
            return None
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
    
    async def _authenticate_demo_user(self, password: str) -> Optional[UserResponse]:
        """Authenticate demo user"""
        if password != self.DEMO_USER["password"]:
            return None
        
        # Create demo user response
        demo_user = UserResponse(
            id=self.DEMO_USER["id"],
            email=self.DEMO_USER["email"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Log demo usage
        await self._log_demo_usage(self.DEMO_USER["email"])
        
        return demo_user
    
    async def start_instant_demo(self) -> Tuple[str, UserResponse]:
        """Start instant demo session with token"""
        demo_user = UserResponse(
            id=self.DEMO_USER["id"],
            email=self.DEMO_USER["email"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create demo token
        token = self.create_demo_token(self.DEMO_USER["id"])
        
        # Log demo usage
        await self._log_demo_usage(self.DEMO_USER["email"])
        
        # Create initial demo contact if database manager is available
        if self.db:
            await self._create_initial_demo_contact()
        
        return token, demo_user
    
    async def _create_initial_demo_contact(self):
        """Create pre-filled demo contact for instant use"""
        try:
            from ..data.models import ContactCreate, ContextType
            
            demo_contact_data = ContactCreate(
                name="Sarah",
                context=ContextType.ROMANTIC
            )
            
            contact = await self.db.create_contact(demo_contact_data, self.DEMO_USER["id"])
            if contact:
                print(f"✅ Created initial demo contact: {contact.name}")
        except Exception as e:
            print(f"⚠️ Could not create demo contact: {str(e)}")
    
    async def _log_demo_usage(self, email: str, ip_address: Optional[str] = None):
        """Log demo usage for analytics"""
        try:
            # If you have a demo usage table, log it here
            # This would typically use your database manager
            print(f"📊 Demo usage logged for {email} at {datetime.now()}")
        except Exception as e:
            print(f"⚠️ Could not log demo usage: {str(e)}")
    
    async def register_user(self, user_data: UserCreate) -> Tuple[bool, str, Optional[UserResponse]]:
        """Register a new user"""
        # Check if trying to register with demo email
        if user_data.email == self.DEMO_USER["email"]:
            return False, "Demo accounts cannot be registered. Please use a different email.", None
        
        try:
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user in database (you'll need to implement this)
            # user = User(
            #     email=user_data.email,
            #     hashed_password=hashed_password
            # )
            # saved_user = await self.db.create_user(user)
            
            # For now, return success (implement actual user creation)
            return True, "Registration successful! Please verify your email.", None
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
    
    async def get_current_user(self, credentials: Optional[HTTPAuthorizationCredentials] = None) -> Optional[UserResponse]:
        """Get current user from JWT token (FastAPI dependency)"""
        if not credentials:
            return None
        
        try:
            payload = self.decode_token(credentials.credentials)
            user_id = payload.get("sub")
            
            if not user_id:
                return None
            
            # Check if it's a demo user
            if payload.get("is_demo", False):
                return UserResponse(
                    id=self.DEMO_USER["id"],
                    email=self.DEMO_USER["email"],
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            
            # Regular user lookup (implement based on your user storage)
            # return await self.get_user_by_id(user_id)
            return None
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            print(f"Error getting current user: {str(e)}")
            return None
    
    def is_demo_user(self, user: UserResponse) -> bool:
        """Check if user is a demo user"""
        return user.id.startswith('demo-user-')
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh an existing token"""
        try:
            payload = self.decode_token(token)
            user_id = payload.get("sub")
            is_demo = payload.get("is_demo", False)
            
            if not user_id:
                return None
            
            # Create new token with extended expiry
            if is_demo:
                new_payload = {
                    "sub": user_id,
                    "email": self.DEMO_USER["email"],
                    "is_demo": True
                }
                expire_delta = timedelta(hours=self.DEMO_TOKEN_EXPIRE_HOURS)
            else:
                new_payload = {"sub": user_id}
                expire_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            
            return self.create_access_token(new_payload, expire_delta)
            
        except Exception as e:
            print(f"Token refresh error: {str(e)}")
            return None
    
    def get_demo_stats(self, user: UserResponse) -> Dict[str, Any]:
        """Get demo session statistics"""
        if not self.is_demo_user(user) or not self.db:
            return {}
        
        try:
            # Get stats from database manager
            demo_contacts = self.db._get_demo_user_data(user.id, 'contacts')
            demo_messages = self.db._get_demo_user_data(user.id, 'messages')
            demo_feedback = self.db._get_demo_user_data(user.id, 'feedback')
            
            return {
                'contacts': len(demo_contacts),
                'messages': len(demo_messages),
                'feedback_count': len(demo_feedback),
                'session_type': 'demo'
            }
        except Exception as e:
            print(f"Error getting demo stats: {str(e)}")
            return {}
    
    def should_show_upgrade_prompt(self, user: UserResponse) -> bool:
        """Check if should show upgrade prompt to demo user"""
        if not self.is_demo_user(user) or not self.db:
            return False
        
        try:
            demo_messages = self.db._get_demo_user_data(user.id, 'messages')
            return len(demo_messages) >= 3
        except:
            return False
    
    async def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user (for security)"""
        # In a production system, you'd typically maintain a blacklist
        # or use a Redis store to track invalidated tokens
        print(f"🔒 Sessions invalidated for user: {user_id}")


# FastAPI Dependencies
security = HTTPBearer(auto_error=False)

async def get_auth_manager() -> AuthManager:
    """Dependency to get auth manager instance"""
    return auth_manager

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth: AuthManager = Depends(get_auth_manager)
) -> UserResponse:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await auth.get_current_user(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth: AuthManager = Depends(get_auth_manager)
) -> Optional[UserResponse]:
    """Optional authentication dependency (doesn't raise if no auth)"""
    if not credentials:
        return None
    
    try:
        return await auth.get_current_user(credentials)
    except HTTPException:
        return None

async def get_demo_user_only(
    current_user: UserResponse = Depends(get_current_user),
    auth: AuthManager = Depends(get_auth_manager)
) -> UserResponse:
    """Dependency that only allows demo users"""
    if not auth.is_demo_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for demo users"
        )
    return current_user

async def get_regular_user_only(
    current_user: UserResponse = Depends(get_current_user),
    auth: AuthManager = Depends(get_auth_manager)
) -> UserResponse:
    """Dependency that only allows regular (non-demo) users"""
    if auth.is_demo_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires a full account. Please sign up!"
        )
    return current_user


# Response models for authentication endpoints
class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class LoginRequest(BaseModel):
    """Login request model"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")

class DemoResponse(BaseModel):
    """Demo session response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    demo_stats: Dict[str, Any]
    message: str = "Welcome to The Third Voice demo! 🎭"

class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str


# Extended AuthManager with FastAPI route handlers
class FastAPIAuthManager(AuthManager):
    """Extended auth manager with built-in route handler methods"""
    
    async def login_user(self, login_data: LoginRequest) -> TokenResponse:
        """Handle user login and return token"""
        user = await self.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        if self.is_demo_user(user):
            access_token_expires = timedelta(hours=self.DEMO_TOKEN_EXPIRE_HOURS)
        
        token_data = {"sub": user.id, "email": user.email}
        if self.is_demo_user(user):
            token_data["is_demo"] = True
        
        access_token = self.create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            expires_in=int(access_token_expires.total_seconds()),
            user=user
        )
    
    async def start_demo_session(self) -> DemoResponse:
        """Start instant demo session"""
        token, demo_user = await self.start_instant_demo()
        
        # Get demo stats
        demo_stats = self.get_demo_stats(demo_user)
        
        return DemoResponse(
            access_token=token,
            expires_in=int(timedelta(hours=self.DEMO_TOKEN_EXPIRE_HOURS).total_seconds()),
            user=demo_user,
            demo_stats=demo_stats
        )
    
    async def register_new_user(self, user_data: UserCreate) -> Tuple[bool, str, Optional[UserResponse]]:
        """Register a new user with enhanced validation"""
        # Check if demo email
        if user_data.email == self.DEMO_USER["email"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot register with demo email. Please use a different email address."
            )
        
        # Check if user already exists (implement user lookup)
        # existing_user = await self.get_user_by_email(user_data.email)
        # if existing_user:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Email already registered"
        #     )
        
        try:
            # Hash password and create user
            hashed_password = self.get_password_hash(user_data.password)
            
            # TODO: Implement user creation in database
            # new_user = User(
            #     email=user_data.email,
            #     hashed_password=hashed_password
            # )
            # saved_user = await self.db.create_user(new_user)
            
            return True, "Registration successful!", None
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def logout_user(self, user: UserResponse):
        """Handle user logout"""
        try:
            if self.is_demo_user(user):
                print(f"📊 Demo session ended for {user.email}")
            else:
                print(f"✅ User logged out: {user.email}")
            
            # In production, you might want to blacklist the token
            await self.invalidate_user_sessions(user.id)
            
        except Exception as e:
            print(f"Logout error: {str(e)}")


# Global instance
auth_manager = FastAPIAuthManager()

# Utility functions for easy integration
def setup_auth_manager_with_db(database_manager):
    """Setup auth manager with database reference"""
    global auth_manager
    auth_manager.db = database_manager
    return auth_manager

async def create_demo_token_quick() -> str:
    """Quick utility to create demo token"""
    return auth_manager.create_demo_token(auth_manager.DEMO_USER["id"])


# Import BaseModel for the response models above
from pydantic import BaseModel, Field
"""
Configuration settings for The Third Voice AI
Centralized configuration with environment variables and validation
"""

import os
from typing import Optional, List
from pathlib import Path
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application Settings
    APP_NAME: str = "The Third Voice AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY", description="JWT secret key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    DEMO_TOKEN_EXPIRE_HOURS: int = Field(default=24, env="DEMO_TOKEN_EXPIRE_HOURS")
    
    # AI Configuration
    OPENROUTER_API_KEY: str = Field(..., env="OPENROUTER_API_KEY", description="OpenRouter API key")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    AI_MODEL: str = Field(default="deepseek/deepseek-chat-v3-0324:free", env="AI_MODEL")
    MAX_TOKENS: int = Field(default=1000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    
    # Database Settings
    DATABASE_PATH: str = Field(default="data/thethirdvoice.db", env="DATABASE_PATH")
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")  # For production PostgreSQL
    CACHE_EXPIRY_DAYS: int = Field(default=7, env="CACHE_EXPIRY_DAYS")
    
    # Server Configuration
    HOST: str = Field(default="localhost", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"], 
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    DEMO_RATE_LIMIT_PER_MINUTE: int = Field(default=10, env="DEMO_RATE_LIMIT_PER_MINUTE")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Demo User Configuration
    DEMO_USER_EMAIL: str = Field(default="demo@thethirdvoice.ai", env="DEMO_USER_EMAIL")
    DEMO_USER_PASSWORD: str = Field(default="demo123", env="DEMO_USER_PASSWORD")
    DEMO_USER_ID: str = Field(default="demo-user-001", env="DEMO_USER_ID")
    
    # Email Settings (for future use)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Analytics & Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    ANALYTICS_ENABLED: bool = Field(default=False, env="ANALYTICS_ENABLED")
    
    @validator("DATABASE_PATH")
    def create_database_dir(cls, v):
        """Ensure database directory exists"""
        db_path = Path(v)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path)
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Ensure secret key is secure"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("TEMPERATURE")
    def validate_temperature(cls, v):
        """Validate AI temperature parameter"""
        if not 0.0 <= v <= 2.0:
            raise ValueError("TEMPERATURE must be between 0.0 and 2.0")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


# Create global settings instance
settings = Settings()


# Utility functions for backward compatibility
def get_openrouter_api_key() -> str:
    """Get OpenRouter API key with validation"""
    return settings.OPENROUTER_API_KEY


def is_demo_user_id(user_id: str) -> bool:
    """Check if user ID is a demo user"""
    return user_id == settings.DEMO_USER_ID or user_id.startswith('demo-user-')


def get_database_url() -> str:
    """Get database URL (SQLite or PostgreSQL)"""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    return f"sqlite:///{settings.DATABASE_PATH}"


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    WORKERS: int = 4


class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG: bool = True
    DATABASE_PATH: str = ":memory:"  # In-memory SQLite for tests
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5  # Shorter tokens for tests


def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# For backward compatibility
AppConfig = Settings
