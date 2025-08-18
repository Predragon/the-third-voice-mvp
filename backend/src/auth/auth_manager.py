"""
Authentication Manager for The Third Voice AI
Handle authentication workflows with Supabase
Enhanced with instant demo access and reduced friction
"""

import streamlit as st
import uuid
from typing import Optional, Tuple
from datetime import datetime, timedelta


class AuthManager:
    """Handle authentication workflows with instant demo access"""
    
    # Single demo user for instant access
    DEMO_USER = {
        "email": "demo@thethirdvoice.ai",
        "password": "demo123",
        "name": "Demo User",
        "id": "demo-user-001"
    }
    
    def __init__(self, db):
        self.db = db
        self.supabase = db.supabase
        # Check for existing session on initialization
        self._check_existing_session()
    
    def _check_existing_session(self):
        """Check if there's an existing Supabase session or demo session"""
        try:
            # Check for demo session first
            if st.session_state.get('is_demo_user', False):
                return  # Demo session already active
                
            # Get current session from Supabase
            session = self.supabase.auth.get_session()
            if session and session.user:
                # Store user in session state if not already there
                if not hasattr(st.session_state, 'user') or st.session_state.user is None:
                    st.session_state.user = session.user
                    print(f"✅ Restored session for user: {session.user.email}")
        except Exception as e:
            print(f"⚠️ Could not check existing session: {str(e)}")
    
    def start_instant_demo(self) -> Tuple[bool, str]:
        """Start instant demo session with no friction"""
        try:
            # Create mock user object for demo
            class MockUser:
                def __init__(self, demo_data):
                    self.id = demo_data["id"]
                    self.email = demo_data["email"]
                    self.user_metadata = {"name": demo_data["name"]}
            
            # Set up demo session
            st.session_state.user = MockUser(self.DEMO_USER)
            st.session_state.is_demo_user = True
            st.session_state.demo_start_time = datetime.now()
            st.session_state.onboarding_completed = True  # Skip onboarding
            
            # Create instant demo contact
            self._create_demo_contact()
            
            # Log demo usage
            self._log_demo_usage(self.DEMO_USER["email"])
            
            return True, f"Welcome to The Third Voice! 🎭"
            
        except Exception as e:
            return False, f"Demo start failed: {str(e)}"
    
    def _create_demo_contact(self):
        """Create a pre-filled demo contact for instant use"""
        user_id = self.DEMO_USER["id"]
        
        # Create demo contact: Sarah (romantic partner)
        demo_contact = self.db.create_contact("Sarah", "romantic", user_id)
        
        if demo_contact:
            # Set as selected contact
            st.session_state.selected_contact = demo_contact
            print(f"✅ Created demo contact: Sarah")
    
    def sign_up(self, email: str, password: str) -> Tuple[bool, str]:
        """Sign up a new user"""
        # Check if trying to sign up with demo credentials
        if email == self.DEMO_USER["email"]:
            return False, "Demo accounts cannot be registered. Please use different email."
            
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, "Check your email for verification link!"
            else:
                return False, "Sign up failed"
                
        except Exception as e:
            return False, f"Sign up error: {str(e)}"
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str]:
        """Sign in user (regular or demo)"""
        # Check if it's a demo login
        if email == self.DEMO_USER["email"]:
            return self._sign_in_demo(email, password)
        
        # Regular Supabase login
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                st.session_state.user = response.user
                st.session_state.is_demo_user = False
                return True, "Successfully signed in!"
            else:
                return False, "Invalid credentials"
                
        except Exception as e:
            return False, f"Sign in error: {str(e)}"
    
    def _sign_in_demo(self, email: str, password: str) -> Tuple[bool, str]:
        """Handle demo user sign in"""
        if password != self.DEMO_USER["password"]:
            return False, "Invalid demo credentials"
        
        return self.start_instant_demo()
    
    def _log_demo_usage(self, email: str):
        """Log demo usage for analytics"""
        try:
            # Insert into demo_usage table
            self.supabase.table("demo_usage").insert({
                "user_email": email,
                "login_time": datetime.now().isoformat(),
                "ip_address": "unknown"
            }).execute()
            
            print(f"📊 Demo usage logged for {email}")
        except Exception as e:
            print(f"⚠️ Could not log demo usage: {str(e)}")
    
    def sign_out(self):
        """Sign out user (regular or demo)"""
        try:
            # Clear demo session data
            if st.session_state.get('is_demo_user', False):
                print("✅ Demo user signed out")
            else:
                # Regular Supabase sign out
                self.supabase.auth.sign_out()
                print("✅ User signed out successfully")
                
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
                
        except Exception as e:
            st.error(f"Sign out error: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (regular or demo)"""
        # Check demo session first (no time limit for smoother UX)
        if st.session_state.get('is_demo_user', False):
            return True
        
        # Check regular session state
        if hasattr(st.session_state, 'user') and st.session_state.user is not None:
            return True
        
        # If not in session state, check Supabase session
        try:
            session = self.supabase.auth.get_session()
            if session and session.user:
                st.session_state.user = session.user
                st.session_state.is_demo_user = False
                return True
        except:
            pass
        
        return False
    
    def is_demo_user(self) -> bool:
        """Check if current user is a demo user"""
        return st.session_state.get('is_demo_user', False)
    
    def get_current_user_id(self) -> Optional[str]:
        """Get current user ID"""
        if self.is_authenticated():
            return st.session_state.user.id
        return None
    
    def get_current_user_email(self) -> Optional[str]:
        """Get current user email"""
        if self.is_authenticated():
            return st.session_state.user.email
        return None
    
    def should_show_upgrade_prompt(self) -> bool:
        """Check if should show upgrade prompt to demo user"""
        if not self.is_demo_user():
            return False
            
        user_id = self.get_current_user_id()
        if not user_id:
            return False
            
        # Show upgrade after 3+ successful interactions
        demo_messages = self.db._get_demo_user_data(user_id, 'messages')
        return len(demo_messages) >= 3
    
    def get_demo_stats(self) -> dict:
        """Get demo session statistics"""
        if not self.is_demo_user():
            return {}
            
        user_id = self.get_current_user_id()
        if not user_id:
            return {}
            
        demo_contacts = len(self.db._get_demo_user_data(user_id, 'contacts'))
        demo_messages = len(self.db._get_demo_user_data(user_id, 'messages'))
        
        return {
            'contacts': demo_contacts,
            'messages': demo_messages
        }
