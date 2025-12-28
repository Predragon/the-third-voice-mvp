"""
Supabase Database Client for The Third Voice AI
Production database with PostgreSQL backend
Compatible interface with DatabaseManager for seamless switching
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import hashlib

from ..core.config import settings

# Import Pydantic schemas for compatibility
from .schemas import (
    ContactCreate, ContactResponse, ContactUpdate,
    MessageCreate, MessageResponse,
    FeedbackCreate, FeedbackResponse,
    AIResponse,
    ContextType, SentimentType, MessageType
)

logger = logging.getLogger(__name__)

# Lazy import supabase to avoid errors when not configured
_supabase_client = None


def get_supabase():
    """Get or create Supabase client (lazy initialization)"""
    global _supabase_client

    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be configured")

        from supabase import create_client
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("✅ Supabase client initialized")

    return _supabase_client


class SupabaseManager:
    """
    Supabase database operations manager.
    Implements the same interface as DatabaseManager for seamless switching.
    """

    def __init__(self):
        self._client = None
        # Demo data storage (same as DatabaseManager)
        self._demo_contacts: Dict[str, List[ContactResponse]] = {}
        self._demo_messages: Dict[str, List[MessageResponse]] = {}
        self._demo_feedback: Dict[str, List[FeedbackResponse]] = {}
        self._demo_cache: Dict[str, Dict[str, Any]] = {}

    @property
    def client(self):
        """Lazy load Supabase client"""
        if self._client is None:
            self._client = get_supabase()
        return self._client

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
        return []

    # ========================
    # User Operations
    # ========================

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            response = self.client.table('users').select('*').eq('email', email).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.client.table('users').select('*').eq('id', user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user by id: {e}")
            return None

    async def create_user(self, email: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            user_data = {
                'email': email,
                'hashed_password': hashed_password,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            response = self.client.table('users').insert(user_data).execute()
            if response.data:
                logger.info(f"✅ Created user: {email}")
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password"""
        try:
            response = self.client.table('users').update({
                'hashed_password': hashed_password,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            response = self.client.table('users').update({
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False

    # ========================
    # Contact Operations (Compatible with DatabaseManager)
    # ========================

    async def get_user_contacts(self, user_id: str) -> List[ContactResponse]:
        """Get all contacts for a user"""
        if self._is_demo_user(user_id):
            return self._get_demo_user_data(user_id, 'contacts')

        try:
            response = self.client.table('contacts').select('*').eq('user_id', user_id).order('updated_at', desc=True).execute()
            if response.data:
                return [
                    ContactResponse(
                        id=c['id'],
                        name=c['name'],
                        context=ContextType(c['context']),
                        user_id=c['user_id'],
                        created_at=datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) if isinstance(c['created_at'], str) else c['created_at'],
                        updated_at=datetime.fromisoformat(c['updated_at'].replace('Z', '+00:00')) if isinstance(c['updated_at'], str) else c['updated_at']
                    )
                    for c in response.data
                ]
            return []
        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            return []

    async def create_contact(self, contact_data: ContactCreate, user_id: str) -> Optional[ContactResponse]:
        """Create a new contact using Pydantic model"""
        if self._is_demo_user(user_id):
            return await self._create_demo_contact(contact_data, user_id)

        try:
            now = datetime.now().isoformat()
            data = {
                'user_id': user_id,
                'name': contact_data.name,
                'context': contact_data.context.value,
                'created_at': now,
                'updated_at': now
            }
            response = self.client.table('contacts').insert(data).execute()
            if response.data:
                c = response.data[0]
                return ContactResponse(
                    id=c['id'],
                    name=c['name'],
                    context=ContextType(c['context']),
                    user_id=c['user_id'],
                    created_at=datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) if isinstance(c['created_at'], str) else c['created_at'],
                    updated_at=datetime.fromisoformat(c['updated_at'].replace('Z', '+00:00')) if isinstance(c['updated_at'], str) else c['updated_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            return None

    async def _create_demo_contact(self, contact_data: ContactCreate, user_id: str) -> ContactResponse:
        """Create demo contact in memory"""
        import uuid
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

    async def get_contact_by_id(self, contact_id: str, user_id: str) -> Optional[ContactResponse]:
        """Get a specific contact"""
        if self._is_demo_user(user_id):
            demo_contacts = self._get_demo_user_data(user_id, 'contacts')
            for contact in demo_contacts:
                if contact.id == contact_id:
                    return contact
            return None

        try:
            response = self.client.table('contacts').select('*').eq('id', contact_id).eq('user_id', user_id).single().execute()
            if response.data:
                c = response.data
                return ContactResponse(
                    id=c['id'],
                    name=c['name'],
                    context=ContextType(c['context']),
                    user_id=c['user_id'],
                    created_at=datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) if isinstance(c['created_at'], str) else c['created_at'],
                    updated_at=datetime.fromisoformat(c['updated_at'].replace('Z', '+00:00')) if isinstance(c['updated_at'], str) else c['updated_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error fetching contact: {e}")
            return None

    async def update_contact(self, contact_id: str, contact_update: ContactUpdate, user_id: str) -> Optional[ContactResponse]:
        """Update a contact using Pydantic model"""
        if self._is_demo_user(user_id):
            return await self._update_demo_contact(contact_id, contact_update, user_id)

        try:
            updates = {'updated_at': datetime.now().isoformat()}
            if contact_update.name is not None:
                updates['name'] = contact_update.name
            if contact_update.context is not None:
                updates['context'] = contact_update.context.value

            response = self.client.table('contacts').update(updates).eq('id', contact_id).eq('user_id', user_id).execute()
            if response.data:
                c = response.data[0]
                return ContactResponse(
                    id=c['id'],
                    name=c['name'],
                    context=ContextType(c['context']),
                    user_id=c['user_id'],
                    created_at=datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) if isinstance(c['created_at'], str) else c['created_at'],
                    updated_at=datetime.fromisoformat(c['updated_at'].replace('Z', '+00:00')) if isinstance(c['updated_at'], str) else c['updated_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error updating contact: {e}")
            return None

    async def _update_demo_contact(self, contact_id: str, contact_update: ContactUpdate, user_id: str) -> Optional[ContactResponse]:
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
        """Delete a contact and related messages"""
        if self._is_demo_user(user_id):
            return await self._delete_demo_contact(contact_id, user_id)

        try:
            # Delete messages first
            self.client.table('messages').delete().eq('contact_id', contact_id).eq('user_id', user_id).execute()
            # Delete cache
            self.client.table('ai_cache').delete().eq('contact_id', contact_id).eq('user_id', user_id).execute()
            # Delete contact
            response = self.client.table('contacts').delete().eq('id', contact_id).eq('user_id', user_id).execute()
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            logger.error(f"Error deleting contact: {e}")
            return False

    async def _delete_demo_contact(self, contact_id: str, user_id: str) -> bool:
        """Delete demo contact and related data"""
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        demo_cache = self._get_demo_user_data(user_id, 'cache')

        demo_contacts[:] = [c for c in demo_contacts if c.id != contact_id]
        demo_messages[:] = [m for m in demo_messages if m.contact_id != contact_id]

        keys_to_remove = [k for k in demo_cache.keys() if k.startswith(f"{contact_id}_")]
        for key in keys_to_remove:
            del demo_cache[key]

        return True

    # ========================
    # Message Operations (Compatible with DatabaseManager)
    # ========================

    async def save_message(self, message_data: MessageCreate, user_id: str,
                          ai_response: AIResponse) -> Optional[MessageResponse]:
        """Save a processed message using Pydantic models"""
        if self._is_demo_user(user_id):
            return await self._save_demo_message(message_data, user_id, ai_response)

        try:
            now = datetime.now().isoformat()
            data = {
                'user_id': user_id,
                'contact_id': message_data.contact_id,
                'contact_name': message_data.contact_name,
                'type': message_data.type.value,
                'original': message_data.original,
                'result': ai_response.transformed_message,
                'sentiment': ai_response.sentiment.value if ai_response.sentiment else None,
                'emotional_state': ai_response.emotional_state,
                'model': ai_response.model_used or settings.AI_MODEL,
                'healing_score': ai_response.healing_score,
                'created_at': now
            }
            response = self.client.table('messages').insert(data).execute()
            if response.data:
                m = response.data[0]
                return MessageResponse(
                    id=m['id'],
                    contact_id=m['contact_id'],
                    contact_name=m['contact_name'],
                    type=MessageType(m['type']),
                    original=m['original'],
                    result=m['result'],
                    sentiment=SentimentType(m['sentiment']) if m.get('sentiment') else None,
                    emotional_state=m.get('emotional_state'),
                    model=m.get('model'),
                    healing_score=m.get('healing_score'),
                    user_id=m['user_id'],
                    created_at=datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')) if isinstance(m['created_at'], str) else m['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None

    async def _save_demo_message(self, message_data: MessageCreate, user_id: str,
                                ai_response: AIResponse) -> MessageResponse:
        """Save demo message in memory"""
        import uuid
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

    async def get_conversation_history(self, contact_id: str, user_id: str, limit: int = 50) -> List[MessageResponse]:
        """Get message history for a contact"""
        if self._is_demo_user(user_id):
            demo_messages = self._get_demo_user_data(user_id, 'messages')
            contact_messages = [msg for msg in demo_messages if msg.contact_id == contact_id]
            return sorted(contact_messages, key=lambda x: x.created_at, reverse=True)[:limit]

        try:
            response = self.client.table('messages').select('*').eq('user_id', user_id).eq('contact_id', contact_id).order('created_at', desc=True).limit(limit).execute()
            if response.data:
                return [
                    MessageResponse(
                        id=m['id'],
                        contact_id=m['contact_id'],
                        contact_name=m['contact_name'],
                        type=MessageType(m['type']),
                        original=m['original'],
                        result=m['result'],
                        sentiment=SentimentType(m['sentiment']) if m.get('sentiment') else None,
                        emotional_state=m.get('emotional_state'),
                        model=m.get('model'),
                        healing_score=m.get('healing_score'),
                        user_id=m['user_id'],
                        created_at=datetime.fromisoformat(m['created_at'].replace('Z', '+00:00')) if isinstance(m['created_at'], str) else m['created_at']
                    )
                    for m in response.data
                ]
            return []
        except Exception as e:
            logger.error(f"Error fetching message history: {e}")
            return []

    async def get_message_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user message statistics"""
        if self._is_demo_user(user_id):
            return await self._get_demo_message_stats(user_id, days)

        try:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            response = self.client.table('messages').select('healing_score, sentiment').eq('user_id', user_id).gte('created_at', since_date).execute()

            messages = response.data if response.data else []
            healing_scores = [m['healing_score'] for m in messages if m.get('healing_score')]

            return {
                'total_messages': len(messages),
                'avg_healing_score': round(sum(healing_scores) / len(healing_scores), 2) if healing_scores else 0,
                'period_days': days,
                'messages_with_scores': len(healing_scores)
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {'total_messages': 0, 'avg_healing_score': 0, 'period_days': days, 'messages_with_scores': 0}

    async def _get_demo_message_stats(self, user_id: str, days: int) -> Dict[str, Any]:
        """Get demo message statistics"""
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        since_date = datetime.now() - timedelta(days=days)

        recent_messages = [msg for msg in demo_messages if msg.created_at >= since_date]
        healing_scores = [msg.healing_score for msg in recent_messages if msg.healing_score is not None]

        return {
            'total_messages': len(recent_messages),
            'avg_healing_score': round(sum(healing_scores) / len(healing_scores), 2) if healing_scores else 0,
            'period_days': days,
            'messages_with_scores': len(healing_scores)
        }

    # ========================
    # Cache Operations (Compatible with DatabaseManager)
    # ========================

    async def check_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check for cached AI response"""
        if self._is_demo_user(user_id):
            return await self._check_demo_cache(contact_id, message_hash, user_id)

        try:
            response = self.client.table('ai_cache').select('*').eq('message_hash', message_hash).eq('contact_id', contact_id).gte('expires_at', datetime.now().isoformat()).single().execute()
            if response.data:
                c = response.data
                return AIResponse(
                    transformed_message=c['response'],
                    healing_score=c.get('healing_score', 0),
                    sentiment=SentimentType(c['sentiment']) if c.get('sentiment') else SentimentType.UNKNOWN,
                    emotional_state=c.get('emotional_state', 'unknown'),
                    explanation="Retrieved from cache",
                    model_used=c.get('model'),
                    model_id=c.get('model')
                )
            return None
        except Exception:
            return None

    async def _check_demo_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check demo cache"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"

        if cache_key in demo_cache:
            entry = demo_cache[cache_key]
            expires_at = datetime.fromisoformat(entry['expires_at']) if isinstance(entry['expires_at'], str) else entry['expires_at']
            if expires_at > datetime.now():
                return AIResponse(
                    transformed_message=entry['response'],
                    healing_score=entry['healing_score'],
                    sentiment=SentimentType(entry['sentiment']),
                    emotional_state=entry['emotional_state'],
                    explanation="Retrieved from demo cache",
                    model_used=entry.get('model', ''),
                    model_id=entry.get('model', '')
                )
            else:
                del demo_cache[cache_key]
        return None

    async def save_to_cache(self, contact_id: str, message_hash: str, context: str,
                           user_id: str, ai_response: AIResponse) -> bool:
        """Save AI response to cache"""
        if self._is_demo_user(user_id):
            return await self._save_to_demo_cache(contact_id, message_hash, context, user_id, ai_response)

        try:
            expires_at = (datetime.now() + timedelta(days=settings.CACHE_EXPIRY_DAYS)).isoformat()
            data = {
                'contact_id': contact_id,
                'user_id': user_id,
                'message_hash': message_hash,
                'context': context,
                'response': ai_response.transformed_message,
                'model': ai_response.model_used or settings.AI_MODEL,
                'healing_score': ai_response.healing_score,
                'sentiment': ai_response.sentiment.value if ai_response.sentiment else None,
                'emotional_state': ai_response.emotional_state,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at
            }
            self.client.table('ai_cache').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False

    async def _save_to_demo_cache(self, contact_id: str, message_hash: str, context: str,
                                 user_id: str, ai_response: AIResponse) -> bool:
        """Save to demo cache"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        cache_key = f"{contact_id}_{message_hash}"
        expires_at = datetime.now() + timedelta(days=settings.CACHE_EXPIRY_DAYS)

        demo_cache[cache_key] = {
            'contact_id': contact_id,
            'message_hash': message_hash,
            'context': context,
            'response': ai_response.transformed_message,
            'healing_score': ai_response.healing_score,
            'model': ai_response.model_used or settings.AI_MODEL,
            'sentiment': ai_response.sentiment.value if ai_response.sentiment else 'unknown',
            'emotional_state': ai_response.emotional_state,
            'expires_at': expires_at
        }
        return True

    async def clean_expired_cache(self, user_id: Optional[str] = None) -> int:
        """Clean expired cache entries"""
        if user_id and self._is_demo_user(user_id):
            return await self._clean_demo_expired_cache(user_id)

        try:
            # Use cleanup function in Supabase
            response = self.client.rpc('cleanup_expired_cache').execute()
            deleted_count = response.data if response.data else 0
            logger.info(f"🧹 Cleaned {deleted_count} expired cache entries")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")
            return 0

    async def _clean_demo_expired_cache(self, user_id: str) -> int:
        """Clean expired demo cache"""
        demo_cache = self._get_demo_user_data(user_id, 'cache')
        now = datetime.now()

        expired_keys = []
        for key, entry in demo_cache.items():
            expires_at = datetime.fromisoformat(entry['expires_at']) if isinstance(entry['expires_at'], str) else entry['expires_at']
            if expires_at < now:
                expired_keys.append(key)

        for key in expired_keys:
            del demo_cache[key]

        return len(expired_keys)

    @staticmethod
    def create_message_hash(original_message: str, context: str) -> str:
        """Create a hash for message caching"""
        combined = f"{original_message.strip()}|{context.strip()}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()

    # ========================
    # Feedback Operations (Compatible with DatabaseManager)
    # ========================

    async def save_feedback(self, feedback_data: FeedbackCreate, user_id: str) -> Optional[FeedbackResponse]:
        """Save user feedback using Pydantic model"""
        if self._is_demo_user(user_id):
            return await self._save_demo_feedback(feedback_data, user_id)

        try:
            now = datetime.now().isoformat()
            data = {
                'user_id': user_id,
                'rating': feedback_data.rating,
                'feedback_text': feedback_data.feedback_text,
                'feature_context': feedback_data.feature_context,
                'created_at': now
            }
            response = self.client.table('feedback').insert(data).execute()
            if response.data:
                f = response.data[0]
                return FeedbackResponse(
                    id=f['id'],
                    rating=f['rating'],
                    feedback_text=f.get('feedback_text'),
                    feature_context=f['feature_context'],
                    user_id=f['user_id'],
                    created_at=datetime.fromisoformat(f['created_at'].replace('Z', '+00:00')) if isinstance(f['created_at'], str) else f['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return None

    async def _save_demo_feedback(self, feedback_data: FeedbackCreate, user_id: str) -> FeedbackResponse:
        """Save demo feedback in memory"""
        import uuid
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

        logger.info(f"📝 Demo feedback: {feedback.rating}/5 stars for {feedback.feature_context}")
        return feedback

    # ========================
    # Demo Usage Operations
    # ========================

    async def log_demo_usage(self, email: str, ip_address: str = None) -> bool:
        """Log demo session"""
        try:
            self.client.table('demo_usage').insert({
                'user_email': email,
                'ip_address': ip_address,
                'login_time': datetime.now().isoformat()
            }).execute()
            logger.info(f"📊 Demo usage logged for {email}")
            return True
        except Exception as e:
            logger.error(f"Error logging demo usage: {e}")
            return False

    # ========================
    # Health Check
    # ========================

    async def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection"""
        try:
            self.client.table('users').select('id').limit(1).execute()
            return {
                'database': True,
                'type': 'supabase',
                'demo_users': len(self._demo_contacts),
                'timestamp': datetime.now()
            }
        except Exception as e:
            return {
                'database': False,
                'type': 'supabase',
                'error': str(e),
                'timestamp': datetime.now()
            }


# Global instance
supabase_manager = SupabaseManager()
