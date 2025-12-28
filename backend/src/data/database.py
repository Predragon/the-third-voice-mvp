"""
FastAPI Database Manager for The Third Voice AI
Integrates Pydantic models with database operations and demo user support
Modernized for FastAPI with proper async support and type safety
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import hashlib
import asyncio
from contextlib import asynccontextmanager

# Import your new Pydantic models
# Import Pydantic schemas
from .schemas import (
    ContactCreate, ContactResponse, ContactUpdate,
    MessageCreate, MessageResponse, MessageUpdate,
    FeedbackCreate, FeedbackResponse,
    AIResponse,
    AIResponseCacheCreate, AIResponseCacheResponse
)

# Import Peewee models and enums
from .models import (
    Contact, Message, AIResponseCache, Feedback,
    SentimentType, ContextType, MessageType

)

# Import Peewee models for database operations (your existing ones)
from .peewee_models import (
    User as PeeweeUser,
    Contact as PeeweeContact,
    Message as PeeweeMessage,
    AIResponseCache as PeeweeAIResponseCache,
    Feedback as PeeweeFeedback,
    DemoUsage as PeeweeDemoUsage,
    get_db_context
)
from ..core.config import settings


class DatabaseManager:
    """FastAPI-compatible database manager with Pydantic integration"""
    
    def __init__(self):
        # Demo data storage (in-memory for demo users)
        self._demo_contacts: Dict[str, List[ContactResponse]] = {}
        self._demo_messages: Dict[str, List[MessageResponse]] = {}
        self._demo_feedback: Dict[str, List[FeedbackResponse]] = {}
        self._demo_cache: Dict[str, Dict[str, Any]] = {}
    
    def _is_demo_user(self, user_id: str) -> bool:
        """Check if this is a demo user"""
        return user_id.startswith('demo-user-')
    
    def _get_demo_user_data(self, user_id: str, data_type: str):
        """Get demo user data structure with proper typing"""
        if data_type == 'contacts':
            return self._demo_contacts.setdefault(user_id, [])
        elif data_type == 'messages':
            return self._demo_messages.setdefault(user_id, [])
        elif data_type == 'feedback':
            return self._demo_feedback.setdefault(user_id, [])
        elif data_type == 'cache':
            return self._demo_cache.setdefault(user_id, {})
        return []
    
    async def get_user_contacts(self, user_id: str) -> List[ContactResponse]:
        """Get all contacts for a user with proper return typing"""
        if self._is_demo_user(user_id):
            return self._get_demo_user_data(user_id, 'contacts')
        
        try:
            with get_db_context():
                peewee_contacts = list(PeeweeContact.select().where(PeeweeContact.user_id == user_id))
                # Convert Peewee models to Pydantic models
                contacts = [
                    ContactResponse(
                        id=contact.id,
                        name=contact.name,
                        context=ContextType(contact.context),
                        user_id=contact.user_id,
                        created_at=contact.created_at,
                        updated_at=contact.updated_at
                    )
                    for contact in peewee_contacts
                ]
                return contacts
        except Exception as e:
            print(f"Error fetching contacts: {str(e)}")
            return []
    
    async def create_contact(self, contact_data: ContactCreate, user_id: str) -> Optional[ContactResponse]:
        """Create a new contact using Pydantic models"""
        if self._is_demo_user(user_id):
            return await self._create_demo_contact(contact_data, user_id)
        
        try:
            with get_db_context():
                peewee_contact = PeeweeContact.create(
                    name=contact_data.name,
                    context=contact_data.context.value,
                    user_id=user_id
                )
                
                # Convert to Pydantic response model
                return ContactResponse(
                    id=peewee_contact.id,
                    name=peewee_contact.name,
                    context=ContextType(peewee_contact.context),
                    user_id=peewee_contact.user_id,
                    created_at=peewee_contact.created_at,
                    updated_at=peewee_contact.updated_at
                )
        except Exception as e:
            print(f"Error creating contact: {str(e)}")
            return None
    
    async def _create_demo_contact(self, contact_data: ContactCreate, user_id: str) -> ContactResponse:
        """Create demo contact in memory"""
        now = datetime.now()
        
        contact = ContactResponse(
            id=str(uuid.uuid4()),
            name=contact_data.name,
            context=contact_data.context,
            user_id=user_id,
            created_at=now,
            updated_at=now
        )
        
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        demo_contacts.append(contact)
        
        return contact
    
    async def save_message(self, message_data: MessageCreate, user_id: str, 
                          ai_response: AIResponse) -> Optional[MessageResponse]:
        """Save a message with AI response data"""
        if self._is_demo_user(user_id):
            return await self._save_demo_message(message_data, user_id, ai_response)
        
        try:
            with get_db_context():
                peewee_message = PeeweeMessage.create(
                    contact_id=message_data.contact_id,
                    contact_name=message_data.contact_name,
                    type=message_data.type.value,
                    original=message_data.original,
                    result=ai_response.transformed_message,
                    sentiment=ai_response.sentiment.value,
                    emotional_state=ai_response.emotional_state,
                    model=ai_response.model_used or settings.AI_MODEL,
                    healing_score=ai_response.healing_score,
                    user_id=user_id
                )
                
                return MessageResponse(
                    id=peewee_message.id,
                    contact_id=peewee_message.contact_id,
                    contact_name=peewee_message.contact_name,
                    type=MessageType(peewee_message.type),
                    original=peewee_message.original,
                    result=peewee_message.result,
                    sentiment=SentimentType(peewee_message.sentiment) if peewee_message.sentiment else None,
                    emotional_state=peewee_message.emotional_state,
                    model=peewee_message.model,
                    healing_score=peewee_message.healing_score,
                    user_id=peewee_message.user_id,
                    created_at=peewee_message.created_at
                )
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            return None
    
    async def _save_demo_message(self, message_data: MessageCreate, user_id: str, 
                                ai_response: AIResponse) -> MessageResponse:
        """Save demo message in memory"""
        message = MessageResponse(
            id=str(uuid.uuid4()),
            contact_id=message_data.contact_id,
            contact_name=message_data.contact_name,
            type=message_data.type,
            original=message_data.original,
            result=ai_response.transformed_message,
            sentiment=ai_response.sentiment,
            emotional_state=ai_response.emotional_state,
            model=ai_response.model_used or settings.AI_MODEL,
            healing_score=ai_response.healing_score,
            user_id=user_id,
            created_at=datetime.now()
        )
        
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        demo_messages.append(message)
        
        return message
    
    async def get_conversation_history(self, contact_id: str, user_id: str, 
                                     limit: int = 50) -> List[MessageResponse]:
        """Get conversation history with proper Pydantic typing"""
        if self._is_demo_user(user_id):
            demo_messages = self._get_demo_user_data(user_id, 'messages')
            contact_messages = [msg for msg in demo_messages if msg.contact_id == contact_id]
            return sorted(contact_messages, key=lambda x: x.created_at, reverse=True)[:limit]
        
        try:
            with get_db_context():
                peewee_messages = list(
                    PeeweeMessage.select()
                    .where(
                        (PeeweeMessage.contact_id == contact_id) & 
                        (PeeweeMessage.user_id == user_id)
                    )
                    .order_by(PeeweeMessage.created_at.desc())
                    .limit(limit)
                )
                
                messages = [
                    MessageResponse(
                        id=msg.id,
                        contact_id=msg.contact_id,
                        contact_name=msg.contact_name,
                        type=MessageType(msg.type),
                        original=msg.original,
                        result=msg.result,
                        sentiment=SentimentType(msg.sentiment) if msg.sentiment else None,
                        emotional_state=msg.emotional_state,
                        model=msg.model,
                        healing_score=msg.healing_score,
                        user_id=msg.user_id,
                        created_at=msg.created_at
                    )
                    for msg in peewee_messages
                ]
                return messages
        except Exception as e:
            print(f"Error fetching conversation history: {str(e)}")
            return []
    
    async def save_feedback(self, feedback_data: FeedbackCreate, user_id: str) -> Optional[FeedbackResponse]:
        """Save user feedback with Pydantic models"""
        if self._is_demo_user(user_id):
            return await self._save_demo_feedback(feedback_data, user_id)
        
        try:
            with get_db_context():
                peewee_feedback = PeeweeFeedback.create(
                    user_id=user_id,
                    rating=feedback_data.rating,
                    feedback_text=feedback_data.feedback_text,
                    feature_context=feedback_data.feature_context
                )
                
                return FeedbackResponse(
                    id=peewee_feedback.id,
                    rating=peewee_feedback.rating,
                    feedback_text=peewee_feedback.feedback_text,
                    feature_context=peewee_feedback.feature_context,
                    user_id=peewee_feedback.user_id,
                    created_at=peewee_feedback.created_at
                )
        except Exception as e:
            print(f"Error saving feedback: {str(e)}")
            return None
    
    async def _save_demo_feedback(self, feedback_data: FeedbackCreate, user_id: str) -> FeedbackResponse:
        """Save demo feedback in memory"""
        feedback = FeedbackResponse(
            id=str(uuid.uuid4()),
            rating=feedback_data.rating,
            feedback_text=feedback_data.feedback_text,
            feature_context=feedback_data.feature_context,
            user_id=user_id,
            created_at=datetime.now()
        )
        
        demo_feedback = self._get_demo_user_data(user_id, 'feedback')
        demo_feedback.append(feedback)
        
        # Log demo feedback for analytics
        print(f"📝 Demo feedback: {feedback.rating}/5 stars for {feedback.feature_context}")
        if feedback.feedback_text:
            print(f"   Comment: {feedback.feedback_text}")
        
        return feedback
    
    async def check_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check for cached AI response"""
        if self._is_demo_user(user_id):
            return await self._check_demo_cache(contact_id, message_hash, user_id)
        
        try:
            with get_db_context():
                cache_entry = (
                    PeeweeAIResponseCache.select()
                    .where(
                        (PeeweeAIResponseCache.contact_id == contact_id) &
                        (PeeweeAIResponseCache.message_hash == message_hash) &
                        (PeeweeAIResponseCache.user_id == user_id) &
                        (PeeweeAIResponseCache.expires_at > datetime.now())
                    )
                    .first()
                )
                
                if cache_entry:
                    return AIResponse(
                        transformed_message=cache_entry.response,
                        healing_score=cache_entry.healing_score or 0,
                        sentiment=SentimentType(cache_entry.sentiment) if cache_entry.sentiment else SentimentType.UNKNOWN,
                        emotional_state=cache_entry.emotional_state or "unknown",
                        explanation="Retrieved from cache",
                        model_used=cache_entry.model,
                        model_id=cache_entry.model
                    )
                return None
        except Exception as e:
            print(f"Error checking cache: {str(e)}")
            return None
    
    async def _check_demo_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check demo cache with proper Pydantic return types"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"
        
        if cache_key in demo_cache:
            cache_entry = demo_cache[cache_key]
            # Check if not expired
            expires_at = datetime.fromisoformat(cache_entry['expires_at']) if isinstance(cache_entry['expires_at'], str) else cache_entry['expires_at']
            
            if expires_at > datetime.now():
                return AIResponse(
                    transformed_message=cache_entry["response"],
                    healing_score=cache_entry["healing_score"],
                    sentiment=SentimentType(cache_entry["sentiment"]),
                    emotional_state=cache_entry["emotional_state"],
                    explanation="Retrieved from demo cache",
                    model_used=cache_entry.get("model", ""),
                    model_id=cache_entry.get("model", "")
                )
            else:
                # Remove expired entry
                del demo_cache[cache_key]
        
        return None
    
    async def save_to_cache(self, contact_id: str, message_hash: str, context: str,
                           user_id: str, ai_response: AIResponse) -> bool:
        """Save AI response to cache"""
        if self._is_demo_user(user_id):
            return await self._save_to_demo_cache(contact_id, message_hash, context, user_id, ai_response)
        
        try:
            with get_db_context():
                expires_at = datetime.now() + timedelta(days=getattr(settings, 'CACHE_EXPIRY_DAYS', 7))
                
                PeeweeAIResponseCache.create(
                    contact_id=contact_id,
                    message_hash=message_hash,
                    context=context,
                    response=ai_response.transformed_message,
                    healing_score=ai_response.healing_score,
                    model=ai_response.model_used or settings.AI_MODEL,
                    sentiment=ai_response.sentiment.value,
                    emotional_state=ai_response.emotional_state,
                    user_id=user_id,
                    expires_at=expires_at
                )
                return True
        except Exception as e:
            print(f"Error saving to cache: {str(e)}")
            return False
    
    async def _save_to_demo_cache(self, contact_id: str, message_hash: str, context: str,
                                 user_id: str, ai_response: AIResponse) -> bool:
        """Save to demo cache with proper datetime handling"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"
        
        expires_at = datetime.now() + timedelta(days=getattr(settings, 'CACHE_EXPIRY_DAYS', 7))
        
        cache_entry = {
            "contact_id": contact_id,
            "message_hash": message_hash,
            "context": context,
            "response": ai_response.transformed_message,
            "healing_score": ai_response.healing_score,
            "model": ai_response.model_used or settings.AI_MODEL,
            "sentiment": ai_response.sentiment.value,
            "emotional_state": ai_response.emotional_state,
            "expires_at": expires_at
        }
        
        demo_cache[cache_key] = cache_entry
        return True
    
    async def update_contact(self, contact_id: str, contact_update: ContactUpdate, 
                           user_id: str) -> Optional[ContactResponse]:
        """Update contact using Pydantic models"""
        if self._is_demo_user(user_id):
            return await self._update_demo_contact(contact_id, contact_update, user_id)
        
        try:
            with get_db_context():
                # Build update data from non-None fields
                update_data = {}
                if contact_update.name is not None:
                    update_data['name'] = contact_update.name
                if contact_update.context is not None:
                    update_data['context'] = contact_update.context.value
                
                if update_data:
                    update_data['updated_at'] = datetime.now()
                    
                    updated_count = (
                        PeeweeContact.update(**update_data)
                        .where(
                            (PeeweeContact.id == contact_id) & 
                            (PeeweeContact.user_id == user_id)
                        )
                        .execute()
                    )
                    
                    if updated_count > 0:
                        # Fetch and return updated contact
                        updated_contact = PeeweeContact.get(
                            (PeeweeContact.id == contact_id) & 
                            (PeeweeContact.user_id == user_id)
                        )
                        return ContactResponse(
                            id=updated_contact.id,
                            name=updated_contact.name,
                            context=ContextType(updated_contact.context),
                            user_id=updated_contact.user_id,
                            created_at=updated_contact.created_at,
                            updated_at=updated_contact.updated_at
                        )
                return None
        except Exception as e:
            print(f"Error updating contact: {str(e)}")
            return None
    
    async def _update_demo_contact(self, contact_id: str, contact_update: ContactUpdate, 
                                  user_id: str) -> Optional[ContactResponse]:
        """Update demo contact in memory"""
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        
        for contact in demo_contacts:
            if contact.id == contact_id:
                if contact_update.name is not None:
                    contact.name = contact_update.name
                if contact_update.context is not None:
                    contact.context = contact_update.context
                contact.updated_at = datetime.now()
                return contact
        
        return None
    
    async def delete_contact(self, contact_id: str, user_id: str) -> bool:
        """Delete a contact and its related data"""
        if self._is_demo_user(user_id):
            return await self._delete_demo_contact(contact_id, user_id)
        
        try:
            with get_db_context():
                # Delete in proper order due to foreign key constraints
                PeeweeMessage.delete().where(
                    (PeeweeMessage.contact_id == contact_id) & 
                    (PeeweeMessage.user_id == user_id)
                ).execute()
                
                PeeweeAIResponseCache.delete().where(
                    (PeeweeAIResponseCache.contact_id == contact_id) & 
                    (PeeweeAIResponseCache.user_id == user_id)
                ).execute()
                
                deleted_count = (
                    PeeweeContact.delete()
                    .where(
                        (PeeweeContact.id == contact_id) & 
                        (PeeweeContact.user_id == user_id)
                    )
                    .execute()
                )
                return deleted_count > 0
        except Exception as e:
            print(f"Error deleting contact: {str(e)}")
            return False
    
    async def _delete_demo_contact(self, contact_id: str, user_id: str) -> bool:
        """Delete demo contact and related data"""
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        
        # Remove contact
        demo_contacts[:] = [c for c in demo_contacts if c.id != contact_id]
        
        # Remove messages
        demo_messages[:] = [m for m in demo_messages if m.contact_id != contact_id]
        
        # Remove cache entries
        keys_to_remove = [k for k in demo_cache.keys() if k.startswith(f"{contact_id}_")]
        for key in keys_to_remove:
            del demo_cache[key]
        
        return True
    
    async def get_contact_by_id(self, contact_id: str, user_id: str) -> Optional[ContactResponse]:
        """Get a specific contact by ID with proper typing"""
        if self._is_demo_user(user_id):
            demo_contacts = self._get_demo_user_data(user_id, 'contacts')
            for contact in demo_contacts:
                if contact.id == contact_id:
                    return contact
            return None
        
        try:
            with get_db_context():
                peewee_contact = (
                    PeeweeContact.select()
                    .where(
                        (PeeweeContact.id == contact_id) & 
                        (PeeweeContact.user_id == user_id)
                    )
                    .first()
                )
                
                if peewee_contact:
                    return ContactResponse(
                        id=peewee_contact.id,
                        name=peewee_contact.name,
                        context=ContextType(peewee_contact.context),
                        user_id=peewee_contact.user_id,
                        created_at=peewee_contact.created_at,
                        updated_at=peewee_contact.updated_at
                    )
                return None
        except Exception as e:
            print(f"Error fetching contact: {str(e)}")
            return None
    
    async def get_message_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get message statistics with proper typing"""
        if self._is_demo_user(user_id):
            return await self._get_demo_message_stats(user_id, days)
        
        try:
            with get_db_context():
                since_date = datetime.now() - timedelta(days=days)
                
                total_messages = (
                    PeeweeMessage.select()
                    .where(
                        (PeeweeMessage.user_id == user_id) &
                        (PeeweeMessage.created_at >= since_date)
                    )
                    .count()
                )
                
                # Calculate average healing score
                messages_with_scores = list(
                    PeeweeMessage.select()
                    .where(
                        (PeeweeMessage.user_id == user_id) &
                        (PeeweeMessage.created_at >= since_date) &
                        (PeeweeMessage.healing_score.is_null(False))
                    )
                )
                
                if messages_with_scores:
                    avg_healing_score = sum(msg.healing_score for msg in messages_with_scores) / len(messages_with_scores)
                else:
                    avg_healing_score = 0.0
                
                return {
                    "total_messages": total_messages,
                    "avg_healing_score": round(avg_healing_score, 2),
                    "period_days": days,
                    "messages_with_scores": len(messages_with_scores)
                }
        except Exception as e:
            print(f"Error getting message stats: {str(e)}")
            return {"total_messages": 0, "avg_healing_score": 0.0, "period_days": days}
    
    async def _get_demo_message_stats(self, user_id: str, days: int) -> Dict[str, Any]:
        """Get demo message statistics"""
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        since_date = datetime.now() - timedelta(days=days)
        
        recent_messages = [
            msg for msg in demo_messages 
            if msg.created_at >= since_date
        ]
        
        total_messages = len(recent_messages)
        
        healing_scores = [
            msg.healing_score for msg in recent_messages 
            if msg.healing_score is not None
        ]
        
        avg_healing_score = sum(healing_scores) / len(healing_scores) if healing_scores else 0.0
        
        return {
            "total_messages": total_messages,
            "avg_healing_score": round(avg_healing_score, 2),
            "period_days": days,
            "messages_with_scores": len(healing_scores)
        }
    
    async def clean_expired_cache(self, user_id: Optional[str] = None) -> int:
        """Clean expired cache entries and return count of cleaned entries"""
        if user_id and self._is_demo_user(user_id):
            return await self._clean_demo_expired_cache(user_id)
        
        try:
            with get_db_context():
                query = PeeweeAIResponseCache.delete().where(
                    PeeweeAIResponseCache.expires_at < datetime.now()
                )
                
                if user_id:
                    query = query.where(PeeweeAIResponseCache.user_id == user_id)
                
                deleted_count = query.execute()
                print(f"🧹 Cleaned {deleted_count} expired cache entries")
                return deleted_count
        except Exception as e:
            print(f"Error cleaning expired cache: {str(e)}")
            return 0
    
    async def _clean_demo_expired_cache(self, user_id: str) -> int:
        """Clean expired demo cache entries"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        now = datetime.now()
        
        expired_keys = []
        for key, entry in demo_cache.items():
            expires_at = datetime.fromisoformat(entry['expires_at']) if isinstance(entry['expires_at'], str) else entry['expires_at']
            if expires_at < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            del demo_cache[key]
        
        if expired_keys:
            print(f"🧹 Cleaned {len(expired_keys)} expired demo cache entries")
        
        return len(expired_keys)
    
    @staticmethod
    def create_message_hash(original_message: str, context: str) -> str:
        """Create a hash for message caching"""
        combined = f"{original_message.strip()}|{context.strip()}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            with get_db_context():
                # Simple query to test database connectivity
                PeeweeContact.select().limit(1).execute()
                return {
                    "database": True,
                    "demo_users": len(self._demo_contacts),
                    "timestamp": datetime.now()
                }
        except Exception as e:
            print(f"Database health check failed: {str(e)}")
            return {
                "database": False,
                "error": str(e),
                "timestamp": datetime.now()
            }

    # ========================
    # User Management Methods
    # ========================

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            with get_db_context():
                user = PeeweeUser.get_or_none(PeeweeUser.email == email)
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "hashed_password": user.hashed_password,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    }
                return None
        except Exception as e:
            print(f"Error fetching user by email: {str(e)}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with get_db_context():
                user = PeeweeUser.get_or_none(PeeweeUser.id == user_id)
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "hashed_password": user.hashed_password,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at
                    }
                return None
        except Exception as e:
            print(f"Error fetching user by id: {str(e)}")
            return None

    async def create_user(self, email: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        """Create a new user in the database"""
        try:
            with get_db_context():
                # Check if user already exists
                existing = PeeweeUser.get_or_none(PeeweeUser.email == email)
                if existing:
                    print(f"User already exists: {email}")
                    return None

                # Create new user
                user = PeeweeUser.create(
                    email=email,
                    hashed_password=hashed_password,
                    is_active=True
                )

                print(f"✅ Created new user: {email}")
                return {
                    "id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None

    async def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password"""
        try:
            with get_db_context():
                updated = PeeweeUser.update(
                    hashed_password=hashed_password,
                    updated_at=datetime.now()
                ).where(PeeweeUser.id == user_id).execute()
                return updated > 0
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        try:
            with get_db_context():
                updated = PeeweeUser.update(
                    is_active=False,
                    updated_at=datetime.now()
                ).where(PeeweeUser.id == user_id).execute()
                return updated > 0
        except Exception as e:
            print(f"Error deactivating user: {str(e)}")
            return False

    async def log_demo_usage(self, email: str, ip_address: Optional[str] = None) -> bool:
        """Log demo user session for analytics"""
        try:
            with get_db_context():
                PeeweeDemoUsage.create(
                    user_email=email,
                    ip_address=ip_address
                )
                print(f"📊 Demo usage logged for {email}")
                return True
        except Exception as e:
            print(f"Error logging demo usage: {str(e)}")
            return False


# Dependency injection for FastAPI
async def get_database_manager() -> DatabaseManager:
    """FastAPI dependency to get database manager instance"""
    return db_manager


# Global instance
db_manager = DatabaseManager()

# Utility functions for FastAPI routes
async def get_user_contacts_list(user_id: str) -> List[ContactResponse]:
    """Utility function for route handlers"""
    return await db_manager.get_user_contacts(user_id)


async def create_new_contact(contact_data: ContactCreate, user_id: str) -> Optional[ContactResponse]:
    """Utility function for contact creation"""
    return await db_manager.create_contact(contact_data, user_id)


async def get_contact_messages(contact_id: str, user_id: str, limit: int = 50) -> List[MessageResponse]:
    """Utility function for getting conversation history"""
    return await db_manager.get_conversation_history(contact_id, user_id, limit)