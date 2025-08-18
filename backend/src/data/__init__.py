"""
Data models and database management for The Third Voice AI
"""

from .models import Contact, Message, AIResponse
from .database import DatabaseManager

__all__ = ['Contact', 'Message', 'AIResponse', 'DatabaseManager']
