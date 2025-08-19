# src/data/__init__.py
"""
Data layer package containing models, database operations, and schemas
"""

from .database import db_manager, get_database_manager
from .schemas import (
    ContactCreate, ContactResponse, ContactUpdate,
    MessageCreate, MessageResponse, 
    UserCreate, UserResponse,
    FeedbackCreate, FeedbackResponse,
    AIResponse
)

__all__ = [
    "db_manager",
    "get_database_manager",
    "ContactCreate", "ContactResponse", "ContactUpdate",
    "MessageCreate", "MessageResponse",
    "UserCreate", "UserResponse", 
    "FeedbackCreate", "FeedbackResponse",
    "AIResponse"
]
