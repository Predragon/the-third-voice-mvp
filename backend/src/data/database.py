"""
Database Management Module for The Third Voice AI
Supabase database wrapper with error handling and demo user support
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from supabase import create_client, Client
import uuid

from .models import Contact, Message, AIResponse
from ..config.settings import AppConfig


class DatabaseManager:
    """Supabase database wrapper with error handling and demo user support"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            AppConfig.get_supabase_url(),
            AppConfig.get_supabase_key()
        )
        
        # Demo data storage (in-memory)
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
        
        # Regular database logic
        try:
            response = self.supabase.table("contacts").select("*").eq("user_id", user_id).execute()
            contacts = []
            for contact_data in response.data:
                contacts.append(Contact(
                    id=contact_data["id"],
                    name=contact_data["name"],
                    context=contact_data["context"],
                    user_id=contact_data["user_id"],
                    created_at=datetime.fromisoformat(contact_data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(contact_data["updated_at"].replace('Z', '+00:00'))
                ))
            return contacts
        except Exception as e:
            st.error(f"Error fetching contacts: {str(e)}")
            return []
    
    def create_contact(self, name: str, context: str, user_id: str) -> Optional[Contact]:
        """Create a new contact (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._create_demo_contact(name, context, user_id)
        
        # Regular database logic
        try:
            contact_data = {
                "name": name,
                "context": context,
                "user_id": user_id
            }
            response = self.supabase.table("contacts").insert(contact_data).execute()
            if response.data:
                data = response.data[0]
                return Contact(
                    id=data["id"],
                    name=data["name"],
                    context=data["context"],
                    user_id=data["user_id"],
                    created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
                )
            return None
        except Exception as e:
            st.error(f"Error creating contact: {str(e)}")
            return None
    
    def _create_demo_contact(self, name: str, context: str, user_id: str) -> Contact:
        """Create demo contact in memory"""
        now = datetime.now()
        contact = Contact(
            id=str(uuid.uuid4()),
            name=name,
            context=context,
            user_id=user_id,
            created_at=now,
            updated_at=now
        )
        
        demo_contacts = self._get_demo_user_data(user_id, 'contacts')
        demo_contacts.append(contact)
        
        return contact
    
    def save_message(self, contact_id: str, contact_name: str, message_type: str,
                    original: str, result: str, user_id: str, ai_response: AIResponse) -> bool:
        """Save a message to the database (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._save_demo_message(contact_id, contact_name, message_type,
                                         original, result, user_id, ai_response)
        
        # Regular database logic
        try:
            message_data = {
                "contact_id": contact_id,
                "contact_name": contact_name,
                "type": message_type,
                "original": original,
                "result": result,
                "sentiment": ai_response.sentiment,
                "emotional_state": ai_response.emotional_state,
                "model": AppConfig.AI_MODEL,
                "healing_score": ai_response.healing_score,
                "user_id": user_id
            }
            response = self.supabase.table("messages").insert(message_data).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error saving message: {str(e)}")
            return False
    
    def _save_demo_message(self, contact_id: str, contact_name: str, message_type: str,
                          original: str, result: str, user_id: str, ai_response: AIResponse) -> bool:
        """Save demo message in memory"""
        message = Message(
            id=str(uuid.uuid4()),
            contact_id=contact_id,
            contact_name=contact_name,
            type=message_type,
            original=original,
            result=result,
            sentiment=ai_response.sentiment,
            emotional_state=ai_response.emotional_state,
            model=AppConfig.AI_MODEL,
            healing_score=ai_response.healing_score,
            user_id=user_id,
            created_at=datetime.now()
        )
        
        demo_messages = self._get_demo_user_data(user_id, 'messages')
        demo_messages.append(message)
        
        return True
    
    def get_conversation_history(self, contact_id: str, user_id: str) -> List[Message]:
        """Get conversation history for a contact (demo-aware)"""
        if self._is_demo_user(user_id):
            demo_messages = self._get_demo_user_data(user_id, 'messages')
            # Filter by contact_id and return most recent (limit 50 like regular version)
            contact_messages = [msg for msg in demo_messages if msg.contact_id == contact_id]
            return sorted(contact_messages, key=lambda x: x.created_at, reverse=True)[:50]
        
        # Regular database logic
        try:
            response = (self.supabase.table("messages")
                       .select("*")
                       .eq("contact_id", contact_id)
                       .eq("user_id", user_id)
                       .order("created_at", desc=True)
                       .limit(50)
                       .execute())
            
            messages = []
            for msg_data in response.data:
                messages.append(Message(
                    id=msg_data["id"],
                    contact_id=msg_data["contact_id"],
                    contact_name=msg_data["contact_name"],
                    type=msg_data["type"],
                    original=msg_data["original"],
                    result=msg_data.get("result"),
                    sentiment=msg_data.get("sentiment"),
                    emotional_state=msg_data.get("emotional_state"),
                    model=msg_data.get("model"),
                    healing_score=msg_data.get("healing_score"),
                    user_id=msg_data["user_id"],
                    created_at=datetime.fromisoformat(msg_data["created_at"].replace('Z', '+00:00'))
                ))
            return messages
        except Exception as e:
            st.error(f"Error fetching conversation history: {str(e)}")
            return []
    
    def save_feedback(self, user_id: str, rating: int, feedback_text: str, feature_context: str) -> bool:
        """Save user feedback (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._save_demo_feedback(user_id, rating, feedback_text, feature_context)
        
        # Regular database logic
        try:
            feedback_data = {
                "user_id": user_id,
                "rating": rating,
                "feedback_text": feedback_text,
                "feature_context": feature_context
            }
            response = self.supabase.table("feedback").insert(feedback_data).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error saving feedback: {str(e)}")
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
        
        # Log demo feedback for analytics (optional)
        print(f"📝 Demo feedback: {rating}/5 stars for {feature_context}")
        if feedback_text:
            print(f"   Comment: {feedback_text}")
        
        return True
    
    def check_cache(self, contact_id: str, message_hash: str, user_id: str) -> Optional[AIResponse]:
        """Check if we have a cached response (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._check_demo_cache(contact_id, message_hash, user_id)
        
        # Regular database logic
        try:
            response = (self.supabase.table("ai_response_cache")
                       .select("*")
                       .eq("contact_id", contact_id)
                       .eq("message_hash", message_hash)
                       .eq("user_id", user_id)
                       .gt("expires_at", datetime.now().isoformat())
                       .execute())
            
            if response.data:
                data = response.data[0]
                return AIResponse(
                    transformed_message=data["response"],
                    healing_score=data["healing_score"],
                    sentiment=data["sentiment"],
                    emotional_state=data["emotional_state"],
                    explanation="From cache"
                )
            return None
        except:
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
        
        # Regular database logic
        try:
            cache_data = {
                "contact_id": contact_id,
                "message_hash": message_hash,
                "context": context,
                "response": response,
                "healing_score": ai_response.healing_score,
                "model": AppConfig.AI_MODEL,
                "sentiment": ai_response.sentiment,
                "emotional_state": ai_response.emotional_state,
                "user_id": user_id,
                "expires_at": (datetime.now() + timedelta(days=AppConfig.CACHE_EXPIRY_DAYS)).isoformat()
            }
            response = self.supabase.table("ai_response_cache").insert(cache_data).execute()
            return len(response.data) > 0
        except:
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
            "model": AppConfig.AI_MODEL,
            "sentiment": ai_response.sentiment,
            "emotional_state": ai_response.emotional_state,
            "expires_at": (datetime.now() + timedelta(days=AppConfig.CACHE_EXPIRY_DAYS)).isoformat()
        }
        
        demo_cache[cache_key] = cache_entry
        return True
    
    def clear_cache_entry(self, contact_id: str, message_hash: str, user_id: str) -> bool:
        """Clear a specific cache entry (demo-aware)"""
        if self._is_demo_user(user_id):
            return self._clear_demo_cache_entry(contact_id, message_hash, user_id)
        
        # Regular database logic
        try:
            response = (self.supabase.table("ai_response_cache")
                       .delete()
                       .eq("contact_id", contact_id)
                       .eq("message_hash", message_hash)
                       .eq("user_id", user_id)
                       .execute())
            return True
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
