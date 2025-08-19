# src/api/routes/__init__.py
"""
API routes package
"""

from . import auth, contacts, messages, feedback, health

__all__ = [
    "auth",
    "contacts", 
    "messages",
    "feedback",
    "health"
]
