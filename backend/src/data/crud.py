# backend/src/data/crud.py
"""
CRUD operations for database models
Clean separation between Peewee models and business logic
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from peewee import DoesNotExist
import hashlib

from .peewee_models import (
    User, Contact, Message, AIResponseCache, Feedback, DemoUsage,
    get_db_context
)
from .schemas import (
    ContactCreate, ContactUpdate, ContactResponse,
    MessageCreate, MessageResponse,
    FeedbackCreate, FeedbackResponse,
    UserCreate, UserResponse,
    SentimentType, ContextType, MessageType
)


class UserCRUD:
    """User CRUD operations"""
    
    @staticmethod
    def create_user(user_data: UserCreate, hashed_password: str) -> Optional[UserResponse]:
        """Create a new user"""
        try:
            with get_db_context():
                user = User.create(
                    email=user_data.email,
                    hashed_password=hashed_password
                )
                return UserResponse(
                    id=user.id,
                    email=user.email,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            with get_db_context():
                user = User.get(User.email == email)
                return UserResponse(
                    id=user.id,
                    email=user.email,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
        except DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            with get_db_context():
                user = User.get(User.id == user_id)
                return UserResponse(
                    id=user.id,
                    email=user.email,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
        except DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: str, **update_fields) -> Optional[UserResponse]:
        """Update user fields"""
        try:
            with get_db_context():
                update_fields['updated_at'] = datetime.now()
                
                updated_count = (
                    User.update(**update_fields)
                    .where(User.id == user_id)
                    .execute()
                )
                
                if updated_count > 0:
                    user = User.get(User.id == user_id)
                    return UserResponse(
                        id=user.id,
                        email=user.email,
                        is_active=user.is_active,
                        created_at=user.created_at,
                        updated_at=user.updated_at
                    )
                return None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None


class ContactCRUD:
    """Contact CRUD operations"""
    
    @staticmethod
    def create_contact(contact_data: ContactCreate, user_id: str) -> Optional[ContactResponse]:
        """Create a new contact"""
        try:
            with get_db_context():
                contact = Contact.create(
                    name=contact_data.name,
                    context=contact_data.context.value,
                    user_id=user_id
                )
                return ContactResponse(
                    id=contact.id,
                    name=contact.name,
                    context=ContextType(contact.context),
                    user_id=contact.user_id,
                    created_at=contact.created_at,
                    updated_at=contact.updated_at
                )
        except Exception as e:
            print(f"Error creating contact: {e}")
            return None
    
    @staticmethod
    def get_user_contacts(user_id: str) -> List[ContactResponse]:
        """Get all contacts for a user"""
        try:
            with get_db_context():
                contacts = list(
                    Contact.select()
                    .where(Contact.user_id == user_id)
                    .order_by(Contact.updated_at.desc())
                )
                return [
                    ContactResponse(
                        id=contact.id,
                        name=contact.name,
                        context=ContextType(contact.context),
                        user_id=contact.user_id,
                        created_at=contact.created_at,
                        updated_at=contact.updated_at
                    )
                    for contact in contacts
                ]
        except Exception as e:
            print(f"Error getting user contacts: {e}")
            return []
    
    @staticmethod
    def get_contact_by_id(contact_id: str, user_id: str) -> Optional[ContactResponse]:
        """Get a specific contact"""
        try:
            with get_db_context():
                contact = Contact.get(
                    (Contact.id == contact_id) & 
                    (Contact.user_id == user_id)
                )
                return ContactResponse(
                    id=contact.id,
                    name=contact.name,
                    context=ContextType(contact.context),
                    user_id=contact.user_id,
                    created_at=contact.created_at,
                    updated_at=contact.updated_at
                )
        except DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting contact: {e}")
            return None
    
    @staticmethod
    def update_contact(contact_id: str, contact_update: ContactUpdate, 
                      user_id: str) -> Optional[ContactResponse]:
        """Update contact information"""
        try:
            with get_db_context():
                # Build update data from non-None fields
                update_data = {'updated_at': datetime.now()}
                
                if contact_update.name is not None:
                    update_data['name'] = contact_update.name
                if contact_update.context is not None:
                    update_data['context'] = contact_update.context.value
                
                if len(update_data) > 1:  # More than just updated_at
                    updated_count = (
                        Contact.update(**update_data)
                        .where(
                            (Contact.id == contact_id) & 
                            (Contact.user_id == user_id)
                        )
                        .execute()
                    )
                    
                    if updated_count > 0:
                        # Fetch and return updated contact
                        contact = Contact.get(
                            (Contact.id == contact_id) & 
                            (Contact.user_id == user_id)
                        )
                        return ContactResponse(
                            id=contact.id,
                            name=contact.name,
                            context=ContextType(contact.context),
                            user_id=contact.user_id,
                            created_at=contact.created_at,
                            updated_at=contact.updated_at
                        )
                return None
        except Exception as e:
            print(f"Error updating contact: {e}")
            return None
    
    @staticmethod
    def delete_contact(contact_id: str, user_id: str) -> bool:
        """Delete a contact and all related data"""
        try:
            with get_db_context():
                # Delete in proper order due to foreign key constraints
                
                # Delete messages
                Message.delete().where(
                    (Message.contact_id == contact_id) & 
                    (Message.user_id == user_id)
                ).execute()
                
                # Delete AI cache
                AIResponseCache.delete().where(
                    (AIResponseCache.contact_id == contact_id) & 
                    (AIResponseCache.user_id == user_id)
                ).execute()
                
                # Delete contact
                deleted_count = (
                    Contact.delete()
                    .where(
                        (Contact.id == contact_id) & 
                        (Contact.user_id == user_id)
                    )
                    .execute()
                )
                
                return deleted_count > 0
        except Exception as e:
            print(f"Error deleting contact: {e}")
            return False


class MessageCRUD:
    """Message CRUD operations"""
    
    @staticmethod
    def create_message(message_data: MessageCreate, user_id: str, 
                      result: str = None, sentiment: SentimentType = None,
                      emotional_state: str = None, model: str = None,
                      healing_score: int = None) -> Optional[MessageResponse]:
        """Create a new message"""
        try:
            with get_db_context():
                message = Message.create(
                    contact_id=message_data.contact_id,
                    contact_name=message_data.contact_name,
                    type=message_data.type.value,
                    original=message_data.original,
                    result=result,
                    sentiment=sentiment.value if sentiment else None,
                    emotional_state=emotional_state,
                    model=model,
                    healing_score=healing_score,
                    user_id=user_id
                )
                
                return MessageResponse(
                    id=message.id,
                    contact_id=message.contact_id,
                    contact_name=message.contact_name,
                    type=MessageType(message.type),
                    original=message.original,
                    result=message.result,
                    sentiment=SentimentType(message.sentiment) if message.sentiment else None,
                    emotional_state=message.emotional_state,
                    model=message.model,
                    healing_score=message.healing_score,
                    user_id=message.user_id,
                    created_at=message.created_at
                )
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    @staticmethod
    def get_conversation_history(contact_id: str, user_id: str, 
                               limit: int = 50) -> List[MessageResponse]:
        """Get conversation history for a contact"""
        try:
            with get_db_context():
                messages = list(
                    Message.select()
                    .where(
                        (Message.contact_id == contact_id) & 
                        (Message.user_id == user_id)
                    )
                    .order_by(Message.created_at.desc())
                    .limit(limit)
                )
                
                return [
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
                    for msg in messages
                ]
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    @staticmethod
    def get_message_by_id(message_id: str, user_id: str) -> Optional[MessageResponse]:
        """Get a specific message"""
        try:
            with get_db_context():
                message = Message.get(
                    (Message.id == message_id) & 
                    (Message.user_id == user_id)
                )
                
                return MessageResponse(
                    id=message.id,
                    contact_id=message.contact_id,
                    contact_name=message.contact_name,
                    type=MessageType(message.type),
                    original=message.original,
                    result=message.result,
                    sentiment=SentimentType(message.sentiment) if message.sentiment else None,
                    emotional_state=message.emotional_state,
                    model=message.model,
                    healing_score=message.healing_score,
                    user_id=message.user_id,
                    created_at=message.created_at
                )
        except DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting message: {e}")
            return None
    
    @staticmethod
    def get_user_message_stats(user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get message statistics for a user"""
        try:
            with get_db_context():
                since_date = datetime.now() - timedelta(days=days)
                
                # Get all messages in time period
                messages = list(
                    Message.select()
                    .where(
                        (Message.user_id == user_id) &
                        (Message.created_at >= since_date)
                    )
                )
                
                total_messages = len(messages)
                
                # Calculate average healing score
                healing_scores = [
                    msg.healing_score for msg in messages 
                    if msg.healing_score is not None
                ]
                avg_healing_score = sum(healing_scores) / len(healing_scores) if healing_scores else 0.0
                
                # Sentiment breakdown
                sentiment_counts = {}
                for msg in messages:
                    if msg.sentiment:
                        sentiment_counts[msg.sentiment] = sentiment_counts.get(msg.sentiment, 0) + 1
                
                return {
                    "total_messages": total_messages,
                    "avg_healing_score": round(avg_healing_score, 2),
                    "period_days": days,
                    "messages_with_scores": len(healing_scores),
                    "sentiment_breakdown": sentiment_counts
                }
        except Exception as e:
            print(f"Error getting message stats: {e}")
            return {
                "total_messages": 0,
                "avg_healing_score": 0.0,
                "period_days": days,
                "messages_with_scores": 0,
                "sentiment_breakdown": {}
            }


class CacheCRUD:
    """AI Response Cache CRUD operations"""
    
    @staticmethod
    def cache_response(contact_id: str, user_id: str, message_hash: str,
                      context: str, response: str, model: str,
                      healing_score: int = None, sentiment: SentimentType = None,
                      emotional_state: str = None) -> bool:
        """Cache an AI response"""
        try:
            with get_db_context():
                expires_at = datetime.now() + timedelta(days=7)
                
                AIResponseCache.create(
                    contact_id=contact_id,
                    message_hash=message_hash,
                    context=context,
                    response=response,
                    healing_score=healing_score,
                    model=model,
                    sentiment=sentiment.value if sentiment else None,
                    emotional_state=emotional_state,
                    user_id=user_id,
                    expires_at=expires_at
                )
                return True
        except Exception as e:
            print(f"Error caching response: {e}")
            return False
    
    @staticmethod
    def get_cached_response(message_hash: str, contact_id: str) -> Optional[AIResponseCache]:
        """Get cached AI response"""
        try:
            with get_db_context():
                cache_entry = AIResponseCache.get(
                    (AIResponseCache.message_hash == message_hash) &
                    (AIResponseCache.contact_id == contact_id) &
                    (AIResponseCache.expires_at > datetime.now())
                )
                return cache_entry
        except DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting cached response: {e}")
            return None
    
    @staticmethod
    def clean_expired_cache(user_id: str = None) -> int:
        """Clean expired cache entries"""
        try:
            with get_db_context():
                query = AIResponseCache.delete().where(
                    AIResponseCache.expires_at < datetime.now()
                )
                
                if user_id:
                    query = query.where(AIResponseCache.user_id == user_id)
                
                deleted_count = query.execute()
                print(f"🧹 Cleaned {deleted_count} expired cache entries")
                return deleted_count
        except Exception as e:
            print(f"Error cleaning expired cache: {e}")
            return 0
    
    @staticmethod
    def create_message_hash(original_message: str, context: str, message_type: str) -> str:
        """Create a hash for message caching"""
        combined = f"{original_message.strip()}|{context.strip()}|{message_type}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()


class FeedbackCRUD:
    """Feedback CRUD operations"""
    
    @staticmethod
    def create_feedback(feedback_data: FeedbackCreate, user_id: str) -> Optional[FeedbackResponse]:
        """Create user feedback"""
        try:
            with get_db_context():
                feedback = Feedback.create(
                    user_id=user_id,
                    rating=feedback_data.rating,
                    feedback_text=feedback_data.feedback_text,
                    feature_context=feedback_data.feature_context
                )
                
                return FeedbackResponse(
                    id=feedback.id,
                    rating=feedback.rating,
                    feedback_text=feedback.feedback_text,
                    feature_context=feedback.feature_context,
                    user_id=feedback.user_id,
                    created_at=feedback.created_at
                )
        except Exception as e:
            print(f"Error creating feedback: {e}")
            return None
    
    @staticmethod
    def get_user_feedback(user_id: str, limit: int = 50) -> List[FeedbackResponse]:
        """Get feedback from a user"""
        try:
            with get_db_context():
                feedback_entries = list(
                    Feedback.select()
                    .where(Feedback.user_id == user_id)
                    .order_by(Feedback.created_at.desc())
                    .limit(limit)
                )
                
                return [
                    FeedbackResponse(
                        id=feedback.id,
                        rating=feedback.rating,
                        feedback_text=feedback.feedback_text,
                        feature_context=feedback.feature_context,
                        user_id=feedback.user_id,
                        created_at=feedback.created_at
                    )
                    for feedback in feedback_entries
                ]
        except Exception as e:
            print(f"Error getting user feedback: {e}")
            return []
    
    @staticmethod
    def get_feedback_stats(days: int = 30) -> Dict[str, Any]:
        """Get feedback statistics"""
        try:
            with get_db_context():
                since_date = datetime.now() - timedelta(days=days)
                
                feedback_entries = list(
                    Feedback.select()
                    .where(Feedback.created_at >= since_date)
                )
                
                if not feedback_entries:
                    return {
                        "total_feedback": 0,
                        "average_rating": 0.0,
                        "rating_breakdown": {},
                        "period_days": days
                    }
                
                total_feedback = len(feedback_entries)
                ratings = [f.rating for f in feedback_entries]
                average_rating = sum(ratings) / len(ratings)
                
                # Rating breakdown
                rating_breakdown = {}
                for rating in ratings:
                    rating_breakdown[rating] = rating_breakdown.get(rating, 0) + 1
                
                return {
                    "total_feedback": total_feedback,
                    "average_rating": round(average_rating, 2),
                    "rating_breakdown": rating_breakdown,
                    "period_days": days
                }
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_breakdown": {},
                "period_days": days
            }


class DemoUsageCRUD:
    """Demo usage tracking CRUD operations"""
    
    @staticmethod
    def log_demo_usage(user_email: str, ip_address: str = None) -> bool:
        """Log demo usage for analytics"""
        try:
            with get_db_context():
                DemoUsage.create(
                    user_email=user_email,
                    ip_address=ip_address
                )
                return True
        except Exception as e:
            print(f"Error logging demo usage: {e}")
            return False
    
    @staticmethod
    def get_demo_stats(days: int = 7) -> Dict[str, Any]:
        """Get demo usage statistics"""
        try:
            with get_db_context():
                since_date = datetime.now() - timedelta(days=days)
                
                demo_sessions = list(
                    DemoUsage.select()
                    .where(DemoUsage.login_time >= since_date)
                )
                
                unique_users = len(set(session.user_email for session in demo_sessions))
                total_sessions = len(demo_sessions)
                
                return {
                    "total_demo_sessions": total_sessions,
                    "unique_demo_users": unique_users,
                    "period_days": days,
                    "sessions_per_user": round(total_sessions / unique_users, 2) if unique_users > 0 else 0
                }
        except Exception as e:
            print(f"Error getting demo stats: {e}")
            return {
                "total_demo_sessions": 0,
                "unique_demo_users": 0,
                "period_days": days,
                "sessions_per_user": 0
            }


# Utility functions for common operations
def get_all_user_data(user_id: str) -> Dict[str, Any]:
    """Get all data for a user (for export/analysis)"""
    try:
        contacts = ContactCRUD.get_user_contacts(user_id)
        
        all_messages = []
        for contact in contacts:
            messages = MessageCRUD.get_conversation_history(contact.id, user_id, limit=1000)
            all_messages.extend(messages)
        
        feedback = FeedbackCRUD.get_user_feedback(user_id)
        message_stats = MessageCRUD.get_user_message_stats(user_id)
        
        return {
            "user_id": user_id,
            "contacts": [contact.dict() for contact in contacts],
            "messages": [msg.dict() for msg in all_messages],
            "feedback": [fb.dict() for fb in feedback],
            "stats": message_stats,
            "export_timestamp": datetime.now()
        }
    except Exception as e:
        print(f"Error getting user data: {e}")
        return {"error": str(e)}


def delete_all_user_data(user_id: str) -> bool:
    """Delete all data for a user (GDPR compliance)"""
    try:
        with get_db_context():
            # Get all contacts first
            contacts = ContactCRUD.get_user_contacts(user_id)
            
            # Delete each contact (which will delete messages and cache)
            for contact in contacts:
                ContactCRUD.delete_contact(contact.id, user_id)
            
            # Delete feedback
            Feedback.delete().where(Feedback.user_id == user_id).execute()
            
            # Delete any remaining cache entries
            AIResponseCache.delete().where(AIResponseCache.user_id == user_id).execute()
            
            # Delete user if not demo user
            if not user_id.startswith('demo-user-'):
                User.delete().where(User.id == user_id).execute()
            
            print(f"✅ All data deleted for user: {user_id}")
            return True
            
    except Exception as e:
        print(f"Error deleting user data: {e}")
        return False
