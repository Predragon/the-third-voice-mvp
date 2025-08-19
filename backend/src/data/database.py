"""
Database Management Module for The Third Voice AI
Peewee ORM wrapper with error handling and demo user support
"""

from datetime import datetime, timedelta
from typing import List, Optional
import uuid
import hashlib

from .database import get_db_context
from .models import Contact, Message, Feedback, AIResponseCache
from ..core.config import settings


class AIResponse:
    """AI Response data structure (keeping from original)"""
    def __init__(self, transformed_message: str, healing_score: float, 
                 sentiment: str, emotional_state: str, explanation: str = ""):
        self.transformed_message = transformed_message
        self.healing_score = healing_score
        self.sentiment = sentiment
        self.emotional_state = emotional_state
        self.explanation = explanation


class DatabaseManager:
    """Peewee database wrapper with error handling and demo user support"""
    
    def __init__(self):
        # Demo data storage (in-memory) - keeping from original
        self._demo_contacts = {}  # {user_id: [contacts]}
        self._demo_messages = {}  # {user_id: [messages]}
        self._demo_feedback = {}  # {user_id: [feedback]}
        self._demo_cache = {}     # {user_id: {cache_key: response}}
    
    def _is_demo_user(self, user_id: str) -> bool:
        """Check if this is a demo user"""
        return user_id.startswith('demo-user-')
    
    def _get_demo_user_data(self, user_id: str, data_type: str):
        """Get demo user data structure"""
        if data_type == 'contacts':
            return self._demo_contacts.setdefault(user_id, [])
        elif data_type == 'messages':
            return self._demo_messages.setdefault(user_id, [])
        elif data_type == 'feedback':
            return self._demo_feedback.setdefault(user_id, [])
        elif data_type == 'cache':
            return self._demo_cache.setdefault(user_id, {})
    
    def get_user_contacts(self, user_id: str) -> List[Contact]:
        """Get all contacts for a user (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._get_demo_user_data(user_id, 'contacts')
        
        # Peewee database logic
        try:
            with get_db_context():
                contacts = list(Contact.select().where(Contact.user_id == user_id))
                return contacts
        except Exception as e:
            print(f"Error fetching contacts: {str(e)}")
            return []
    
    def create_contact(self, name: str, context: str, user_id: str) -> Optional[Contact]:
        """Create a new contact (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._create_demo_contact(name, context, user_id)
        
        # Peewee database logic
        try:
            with get_db_context():
                contact = Contact.create(
                    name=name,
                    context=context,
                    user_id=user_id
                )
                return contact
        except Exception as e:
            print(f"Error creating contact: {str(e)}")
            return None
    
    def _create_demo_contact(self, name: str, context: str, user_id: str) -> Contact:
        """Create demo contact in memory"""
        now = datetime.now()
        
        # Create a mock Contact object (assuming your Contact model has these fields)
        contact = type('Contact', (), {
            'id': str(uuid.uuid4()),
            'name': name,
            'context': context,
            'user_id': user_id,
            'created_at': now,
            'updated_at': now
        })()
        
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        demo_contacts.append(contact)
        
        return contact
    
    def save_message(self, contact_id: str, contact_name: str, message_type: str,
                    original: str, result: str, user_id: str, ai_response: AIResponse) -> bool:
        """Save a message to the database (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._save_demo_message(contact_id, contact_name, message_type,
                                         original, result, user_id, ai_response)
        
        # Peewee database logic
        try:
            with get_db_context():
                Message.create(
                    contact_id=contact_id,
                    contact_name=contact_name,
                    type=message_type,
                    original=original,
                    result=result,
                    sentiment=ai_response.sentiment,
                    emotional_state=ai_response.emotional_state,
                    model=settings.AI_MODEL,
                    healing_score=ai_response.healing_score,
                    user_id=user_id
                )
                return True
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            return False
    
    def _save_demo_message(self, contact_id: str, contact_name: str, message_type: str,
                          original: str, result: str, user_id: str, ai_response: AIResponse) -> bool:
        """Save demo message in memory"""
        message = type('Message', (), {
            'id': str(uuid.uuid4()),
            'contact_id': contact_id,
            'contact_name': contact_name,
            'type': message_type,
            'original': original,
            'result': result,
            'sentiment': ai_response.sentiment,
            'emotional_state': ai_response.emotional_state,
            'model': settings.AI_MODEL,
            'healing_score': ai_response.healing_score,
            'user_id': user_id,
            'created_at': datetime.now()
        })()
        
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        demo_messages.append(message)
        
        return True
    
    def get_conversation_history(self, contact_id: str, user_id: str) -> List[Message]:
        """Get conversation history for a contact (demo-aware)"""
        if self._is_demo_user(user_id):
            demo_messages = self._get_demo_user_data(user_id, 'messages')
            # Filter by contact_id and return most recent (limit 50)
            contact_messages = [msg for msg in demo_messages if msg.contact_id == contact_id]
            return sorted(contact_messages, key=lambda x: x.created_at, reverse=True)[:50]
        
        # Peewee database logic
        try:
            with get_db_context():
                messages = list(
                    Message.select()
                    .where(
                        (Message.contact_id == contact_id) & 
                        (Message.user_id == user_id)
                    )
                    .order_by(Message.created_at.desc())
                    .limit(50)
                )
                return messages
        except Exception as e:
            print(f"Error fetching conversation history: {str(e)}")
            return []
    
    def save_feedback(self, user_id: str, rating: int, feedback_text: str, feature_context: str) -> bool:
        """Save user feedback (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._save_demo_feedback(user_id, rating, feedback_text, feature_context)
        
        # Peewee database logic
        try:
            with get_db_context():
                Feedback.create(
                    user_id=user_id,
                    rating=rating,
                    feedback_text=feedback_text,
                    feature_context=feature_context
                )
                return True
        except Exception as e:
            print(f"Error saving feedback: {str(e)}")
            return False
    
    def _save_demo_feedback(self, user_id: str, rating: int, feedback_text: str, feature_context: str) -> bool:
        """Save demo feedback in memory"""
        feedback = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "feature_context": feature_context,
            "created_at": datetime.now().isoformat()
        }
        
        demo_feedback = self._get_demo_user_data(user_id, 'feedback')
        demo_feedback.append(feedback)
        
        # Log demo feedback for analytics
        print(f"📝 Demo feedback: {rating}/5 stars for {feature_context}")
        if feedback_text:
            print(f"   Comment: {feedback_text}")
        
        return True
    
    def check_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check if we have a cached response (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._check_demo_cache(contact_id, message_hash, user_id)
        
        # Peewee database logic
        try:
            with get_db_context():
                cache_entry = (
                    AIResponseCache.select()
                    .where(
                        (AIResponseCache.contact_id == contact_id) &
                        (AIResponseCache.message_hash == message_hash) &
                        (AIResponseCache.user_id == user_id) &
                        (AIResponseCache.expires_at > datetime.now())
                    )
                    .first()
                )
                
                if cache_entry:
                    return AIResponse(
                        transformed_message=cache_entry.response,
                        healing_score=cache_entry.healing_score,
                        sentiment=cache_entry.sentiment,
                        emotional_state=cache_entry.emotional_state,
                        explanation="From cache"
                    )
                return None
        except Exception as e:
            print(f"Error checking cache: {str(e)}")
            return None
    
    def _check_demo_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check demo cache"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"
        
        if cache_key in demo_cache:
            cache_entry = demo_cache[cache_key]
            # Check if not expired
            if datetime.fromisoformat(cache_entry['expires_at']) > datetime.now():
                return AIResponse(
                    transformed_message=cache_entry["response"],
                    healing_score=cache_entry["healing_score"],
                    sentiment=cache_entry["sentiment"],
                    emotional_state=cache_entry["emotional_state"],
                    explanation="From cache"
                )
            else:
                # Remove expired entry
                del demo_cache[cache_key]
        
        return None
    
    def save_to_cache(self, contact_id: str, message_hash: str, context: str,
                     response: str, user_id: str, ai_response: AIResponse) -> bool:
        """Save response to cache (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._save_to_demo_cache(contact_id, message_hash, context,
                                          response, user_id, ai_response)
        
        # Peewee database logic
        try:
            with get_db_context():
                expires_at = datetime.now() + timedelta(days=settings.CACHE_EXPIRY_DAYS)
                
                AIResponseCache.create(
                    contact_id=contact_id,
                    message_hash=message_hash,
                    context=context,
                    response=response,
                    healing_score=ai_response.healing_score,
                    model=settings.AI_MODEL,
                    sentiment=ai_response.sentiment,
                    emotional_state=ai_response.emotional_state,
                    user_id=user_id,
                    expires_at=expires_at
                )
                return True
        except Exception as e:
            print(f"Error saving to cache: {str(e)}")
            return False
    
    def _save_to_demo_cache(self, contact_id: str, message_hash: str, context: str,
                           response: str, user_id: str, ai_response: AIResponse) -> bool:
        """Save to demo cache"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"
        
        cache_entry = {
            "contact_id": contact_id,
            "message_hash": message_hash,
            "context": context,
            "response": response,
            "healing_score": ai_response.healing_score,
            "model": settings.AI_MODEL,
            "sentiment": ai_response.sentiment,
            "emotional_state": ai_response.emotional_state,
            "expires_at": (datetime.now() + timedelta(days=settings.CACHE_EXPIRY_DAYS)).isoformat()
        }
        
        demo_cache[cache_key] = cache_entry
        return True
    
    def clear_cache_entry(self, contact_id: str, message_hash: str, user_id: str) -> bool:
        """Clear a specific cache entry (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._clear_demo_cache_entry(contact_id, message_hash, user_id)
        
        # Peewee database logic
        try:
            with get_db_context():
                deleted_count = (
                    AIResponseCache.delete()
                    .where(
                        (AIResponseCache.contact_id == contact_id) &
                        (AIResponseCache.message_hash == message_hash) &
                        (AIResponseCache.user_id == user_id)
                    )
                    .execute()
                )
                return deleted_count > 0
        except Exception as e:
            print(f"Error clearing cache entry: {str(e)}")
            return False
    
    def _clear_demo_cache_entry(self, contact_id: str, message_hash: str, user_id: str) -> bool:
        """Clear demo cache entry"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"
        
        if cache_key in demo_cache:
            del demo_cache[cache_key]
        
        return True
    
    def update_contact(self, contact_id: str, name: str, context: str, user_id: str) -> bool:
        """Update an existing contact (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._update_demo_contact(contact_id, name, context, user_id)
        
        try:
            with get_db_context():
                updated_count = (
                    Contact.update(
                        name=name,
                        context=context,
                        updated_at=datetime.now()
                    )
                    .where(
                        (Contact.id == contact_id) & 
                        (Contact.user_id == user_id)
                    )
                    .execute()
                )
                return updated_count > 0
        except Exception as e:
            print(f"Error updating contact: {str(e)}")
            return False
    
    def _update_demo_contact(self, contact_id: str, name: str, context: str, user_id: str) -> bool:
        """Update demo contact in memory"""
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        
        for contact in demo_contacts:
            if contact.id == contact_id:
                contact.name = name
                contact.context = context
                contact.updated_at = datetime.now()
                return True
        
        return False
    
    def delete_contact(self, contact_id: str, user_id: str) -> bool:
        """Delete a contact and its messages (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._delete_demo_contact(contact_id, user_id)
        
        try:
            with get_db_context():
                # Delete messages first (foreign key constraint)
                Message.delete().where(
                    (Message.contact_id == contact_id) & 
                    (Message.user_id == user_id)
                ).execute()
                
                # Delete cache entries
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
            print(f"Error deleting contact: {str(e)}")
            return False
    
    def _delete_demo_contact(self, contact_id: str, user_id: str) -> bool:
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
    
    def get_contact_by_id(self, contact_id: str, user_id: str) -> Optional[Contact]:
        """Get a specific contact by ID (demo-aware)"""
        if self._is_demo_user(user_id):
            demo_contacts = self._get_demo_user_data(user_id, 'contacts')
            for contact in demo_contacts:
                if contact.id == contact_id:
                    return contact
            return None
        
        try:
            with get_db_context():
                contact = (
                    Contact.select()
                    .where(
                        (Contact.id == contact_id) & 
                        (Contact.user_id == user_id)
                    )
                    .first()
                )
                return contact
        except Exception as e:
            print(f"Error fetching contact: {str(e)}")
            return None
    
    def clean_expired_cache(self, user_id: str = None) -> bool:
        """Clean expired cache entries (demo-aware)"""
        if user_id and self._is_demo_user(user_id):
            return self._clean_demo_expired_cache(user_id)
        
        try:
            with get_db_context():
                deleted_count = (
                    AIResponseCache.delete()
                    .where(AIResponseCache.expires_at < datetime.now())
                    .execute()
                )
                print(f"Cleaned {deleted_count} expired cache entries")
                return True
        except Exception as e:
            print(f"Error cleaning expired cache: {str(e)}")
            return False
    
    def _clean_demo_expired_cache(self, user_id: str) -> bool:
        """Clean expired demo cache entries"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        now = datetime.now()
        
        expired_keys = []
        for key, entry in demo_cache.items():
            if datetime.fromisoformat(entry['expires_at']) < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            del demo_cache[key]
        
        if expired_keys:
            print(f"Cleaned {len(expired_keys)} expired demo cache entries")
        
        return True
    
    def get_message_stats(self, user_id: str, days: int = 30) -> dict:
        """Get message statistics for the user (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._get_demo_message_stats(user_id, days)
        
        try:
            with get_db_context():
                since_date = datetime.now() - timedelta(days=days)
                
                total_messages = (
                    Message.select()
                    .where(
                        (Message.user_id == user_id) &
                        (Message.created_at >= since_date)
                    )
                    .count()
                )
                
                avg_healing_score = (
                    Message.select()
                    .where(
                        (Message.user_id == user_id) &
                        (Message.created_at >= since_date) &
                        (Message.healing_score.is_null(False))
                    )
                    .scalar(fn.AVG(Message.healing_score)) or 0.0
                )
                
                return {
                    "total_messages": total_messages,
                    "avg_healing_score": round(avg_healing_score, 2),
                    "period_days": days
                }
        except Exception as e:
            print(f"Error getting message stats: {str(e)}")
            return {"total_messages": 0, "avg_healing_score": 0.0, "period_days": days}
    
    def _get_demo_message_stats(self, user_id: str, days: int) -> dict:
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
            if hasattr(msg, 'healing_score') and msg.healing_score is not None
        ]
        
        avg_healing_score = sum(healing_scores) / len(healing_scores) if healing_scores else 0.0
        
        return {
            "total_messages": total_messages,
            "avg_healing_score": round(avg_healing_score, 2),
            "period_days": days
        }
    
    @staticmethod
    def create_message_hash(original_message: str, context: str) -> str:
        """Create a hash for message caching"""
        combined = f"{original_message}|{context}"
        return hashlib.md5(combined.encode()).hexdigest()


# Global instance
db_manager = DatabaseManager()
