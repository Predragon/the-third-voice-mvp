"""
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
from pydantic import BaseModel, Field

# Change imports to use new structure
from ..data.schemas import UserCreate, UserResponse, ContactCreate, ContextType
from ..core.config import settings

class AuthManager:
    """FastAPI-compatible authentication manager with demo user support"""

    def __init__(self, database_manager=None):
        self.db = database_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer(auto_error=False)

        # JWT settings
        self.SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key-change-in-production')
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
        self.DEMO_TOKEN_EXPIRE_HOURS = getattr(settings, 'DEMO_TOKEN_EXPIRE_HOURS', 24)

    @property
    def DEMO_USER(self):
        """Demo user configuration - loaded from environment via settings"""
        return {
            "email": getattr(settings, 'DEMO_EMAIL', 'demo@thethirdvoice.ai'),
            "password": getattr(settings, 'DEMO_PASSWORD', 'demo123'),
            "name": "Demo User",
            "id": "demo-user-001"
        }

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
        except jwt.exceptions.InvalidTokenError:
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

        # Regular user authentication - query database
        try:
            if not self.db:
                print("Database manager not initialized")
                return None

            user_data = await self.db.get_user_by_email(email)
            if user_data and self.verify_password(password, user_data["hashed_password"]):
                if not user_data.get("is_active", True):
                    print(f"User account deactivated: {email}")
                    return None

                return UserResponse(
                    id=user_data["id"],
                    email=user_data["email"],
                    is_active=user_data["is_active"],
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                )
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
            from ..data.schemas import ContactCreate, ContextType

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
            if self.db:
                await self.db.log_demo_usage(email, ip_address)
            else:
                print(f"📊 Demo usage logged for {email} at {datetime.now()}")
        except Exception as e:
            print(f"⚠️ Could not log demo usage: {str(e)}")

    async def register_user(self, user_data: UserCreate) -> Tuple[bool, str, Optional[UserResponse]]:
        """Register a new user"""
        # Check if trying to register with demo email
        if user_data.email == self.DEMO_USER["email"]:
            return False, "Demo accounts cannot be registered. Please use a different email.", None

        try:
            if not self.db:
                return False, "Database not initialized", None

            # Check if user already exists
            existing_user = await self.db.get_user_by_email(user_data.email)
            if existing_user:
                return False, "Email already registered. Please login or use a different email.", None

            # Hash password
            hashed_password = self.get_password_hash(user_data.password)

            # Create user in database
            user_data_result = await self.db.create_user(user_data.email, hashed_password)

            if user_data_result:
                user_response = UserResponse(
                    id=user_data_result["id"],
                    email=user_data_result["email"],
                    is_active=user_data_result["is_active"],
                    created_at=user_data_result["created_at"],
                    updated_at=user_data_result["updated_at"]
                )
                return True, "Registration successful! Welcome to The Third Voice.", user_response

            return False, "Registration failed. Please try again.", None

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

            # Regular user lookup from database
            if self.db:
                user_data = await self.db.get_user_by_id(user_id)
                if user_data and user_data.get("is_active", True):
                    return UserResponse(
                        id=user_data["id"],
                        email=user_data["email"],
                        is_active=user_data["is_active"],
                        created_at=user_data["created_at"],
                        updated_at=user_data["updated_at"]
                    )
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

    async def request_password_reset(self, email: str) -> bool:
        """Request password reset - generates token and sends email"""
        try:
            if not self.db:
                return False

            # Check if user exists
            user_data = await self.db.get_user_by_email(email)
            if not user_data:
                # Return True to prevent email enumeration, but don't actually send
                return True

            # Generate reset token (valid for 1 hour)
            reset_token = self.create_access_token(
                {"sub": user_data["id"], "type": "password_reset", "email": email},
                expires_delta=timedelta(hours=1)
            )

            # Store reset token in database
            await self.db.store_reset_token(user_data["id"], reset_token)

            # Send email (placeholder - would integrate with email service)
            print(f"📧 Password reset token for {email}: {reset_token[:20]}...")
            # In production: send_email(email, reset_link=f"https://thethirdvoice.ai/reset?token={reset_token}")

            return True
        except Exception as e:
            print(f"Password reset request error: {str(e)}")
            return False

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        try:
            # Decode and validate token
            payload = self.decode_token(token)

            if payload.get("type") != "password_reset":
                return False

            user_id = payload.get("sub")
            if not user_id or not self.db:
                return False

            # Hash new password and update
            hashed_password = self.get_password_hash(new_password)
            success = await self.db.update_user_password(user_id, hashed_password)

            if success:
                # Invalidate all existing sessions
                await self.invalidate_user_sessions(user_id)
                # Clear reset token
                await self.db.clear_reset_token(user_id)

            return success
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            return False

    async def send_verification_email(self, email: str) -> bool:
        """Send email verification link"""
        try:
            if not self.db:
                return False

            user_data = await self.db.get_user_by_email(email)
            if not user_data:
                return False

            # Check if already verified
            if user_data.get("email_verified", False):
                return True

            # Generate verification token (valid for 24 hours)
            verify_token = self.create_access_token(
                {"sub": user_data["id"], "type": "email_verify", "email": email},
                expires_delta=timedelta(hours=24)
            )

            # Store verification token
            await self.db.store_verification_token(user_data["id"], verify_token)

            # Send email (placeholder)
            print(f"📧 Verification token for {email}: {verify_token[:20]}...")
            # In production: send_email(email, verify_link=f"https://thethirdvoice.ai/verify?token={verify_token}")

            return True
        except Exception as e:
            print(f"Verification email error: {str(e)}")
            return False

    async def verify_email(self, token: str) -> bool:
        """Verify email using token"""
        try:
            # Decode and validate token
            payload = self.decode_token(token)

            if payload.get("type") != "email_verify":
                return False

            user_id = payload.get("sub")
            if not user_id or not self.db:
                return False

            # Mark email as verified
            success = await self.db.verify_user_email(user_id)

            if success:
                # Clear verification token
                await self.db.clear_verification_token(user_id)

            return success
        except Exception as e:
            print(f"Email verification error: {str(e)}")
            return False

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

        # Use the parent class method which now has full database support
        return await self.register_user(user_data)

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
