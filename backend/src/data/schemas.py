# backend/src/data/schemas.py
"""
Pydantic models for API request/response validation
Separate from Peewee database models for clean architecture
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums (shared between database and API)
class ContextType(str, Enum):
    ROMANTIC = "romantic"
    COPARENTING = "coparenting"
    WORKPLACE = "workplace"
    FAMILY = "family"
    FRIEND = "friend"


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class MessageType(str, Enum):
    TRANSFORM = "transform"
    INTERPRET = "interpret"


# Base response model
class BaseResponse(BaseModel):
    """Base response with common fields"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User models
class UserBase(BaseModel):
    email: str = Field(..., description="User email address")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email address')
        return v.lower()


class UserResponse(BaseResponse):
    email: str
    is_active: bool = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None


# Contact models
class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Contact name")
    context: ContextType = Field(..., description="Relationship context")


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    context: Optional[ContextType] = None


class ContactResponse(BaseResponse):
    name: str
    context: ContextType
    user_id: str
    
    # Optional computed fields
    message_count: Optional[int] = Field(None, description="Total messages for this contact")
    last_message_date: Optional[datetime] = Field(None, description="Date of last message")


# Message models
class MessageBase(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    contact_name: str = Field(..., description="Contact name for display")
    type: MessageType = Field(..., description="Message type")
    original: str = Field(..., min_length=1, description="Original message text")


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    original: Optional[str] = Field(None, min_length=1)
    result: Optional[str] = None


class MessageResponse(BaseResponse):
    contact_id: str
    contact_name: str
    type: MessageType
    original: str
    result: Optional[str] = None
    sentiment: Optional[SentimentType] = None
    emotional_state: Optional[str] = None
    model: Optional[str] = None
    healing_score: Optional[int] = Field(None, ge=0, le=10, description="Healing score 0-10")
    user_id: str


# AI Response models
class AIResponse(BaseModel):
    """AI processing response"""
    transformed_message: str = Field(..., description="AI-transformed message")
    healing_score: int = Field(5, ge=0, le=10, description="Healing effectiveness score")
    sentiment: SentimentType = Field(SentimentType.NEUTRAL, description="Message sentiment")
    emotional_state: str = Field("understanding", description="Emotional state detected")
    explanation: str = Field("", description="Why this transformation helps")
    subtext: str = Field("", description="Hidden meaning or subtext")
    needs: List[str] = Field(default_factory=list, description="Emotional needs identified")
    warnings: List[str] = Field(default_factory=list, description="Potential concerns")
    model_used: str = Field("", description="AI model that generated response")
    model_id: str = Field("", description="AI model ID")


# Feedback models
class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    feature_context: str = Field(..., description="Which feature this feedback is for")


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(BaseResponse):
    rating: int
    feedback_text: Optional[str]
    feature_context: str
    user_id: str


# Cache models
class AIResponseCacheBase(BaseModel):
    contact_id: str
    message_hash: str
    context: str
    response: str
    model: str


class AIResponseCacheCreate(AIResponseCacheBase):
    healing_score: Optional[int] = None
    sentiment: Optional[SentimentType] = None
    emotional_state: Optional[str] = None
    user_id: str
    expires_at: Optional[datetime] = None


class AIResponseCacheResponse(BaseResponse):
    contact_id: str
    message_hash: str
    context: str
    response: str
    healing_score: Optional[int]
    model: str
    sentiment: Optional[SentimentType]
    emotional_state: Optional[str]
    user_id: str
    expires_at: datetime


# Authentication models
class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LoginRequest(BaseModel):
    """Login request model"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class DemoResponse(BaseModel):
    """Demo session response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    demo_stats: Dict[str, Any]
    message: str = "Welcome to The Third Voice demo! 🎭"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# Statistics and analytics models
class UserStats(BaseModel):
    """User usage statistics"""
    total_messages: int = 0
    total_contacts: int = 0
    avg_healing_score: float = 0.0
    messages_this_week: int = 0
    messages_this_month: int = 0
    most_used_context: Optional[ContextType] = None
    account_age_days: int = 0


class MessageStats(BaseModel):
    """Message processing statistics"""
    total_messages: int
    avg_healing_score: float
    period_days: int
    messages_with_scores: int
    sentiment_breakdown: Dict[str, int] = Field(default_factory=dict)
    context_breakdown: Dict[str, int] = Field(default_factory=dict)


class SystemStats(BaseModel):
    """System-wide statistics"""
    total_users: int
    demo_users: int
    total_messages_today: int
    total_messages_all_time: int
    average_healing_score: float
    most_popular_context: Optional[str] = None
    uptime_seconds: float


# Error response models
class ErrorDetail(BaseModel):
    """Error detail structure"""
    type: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    detail: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Health check model
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    database: bool
    ai_engine: bool
    timestamp: datetime
    version: str
    uptime_seconds: float
    demo_users_active: int = 0


# Bulk operation models
class BulkMessageRequest(BaseModel):
    """Process multiple messages at once"""
    messages: List[MessageCreate] = Field(..., max_items=10)


class BulkMessageResponse(BaseModel):
    """Response for bulk message processing"""
    results: List[MessageResponse]
    failed: List[Dict[str, Any]] = Field(default_factory=list)
    total_processed: int
    success_count: int
    error_count: int


# Export and import models
class ContactExport(BaseModel):
    """Contact export format"""
    contacts: List[ContactResponse]
    messages: List[MessageResponse]
    export_date: datetime
    user_id: str


class ContactImport(BaseModel):
    """Contact import format"""
    contacts: List[ContactCreate]
    validate_only: bool = False


# Pagination models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    size: int = Field(20, ge=1, le=100, description="Items per page (max 100)")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    
    @validator('pages', always=True)
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        size = values.get('size', 20)
        return (total + size - 1) // size if total > 0 else 0


# WebSocket models
class WSMessage(BaseModel):
    """WebSocket message format"""
    type: str  # 'message_processing', 'demo_stats', 'error', etc.
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class WSMessageProcessing(BaseModel):
    """WebSocket message for real-time processing updates"""
    contact_id: str
    status: str  # 'processing', 'complete', 'error'
    progress: Optional[int] = None  # 0-100
    result: Optional[MessageResponse] = None
    error: Optional[str] = None
