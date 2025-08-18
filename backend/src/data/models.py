"""
Data Models for The Third Voice AI
Defines the core data structures used throughout the application
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Contact:
    """Contact data model"""
    id: str
    name: str
    context: str
    user_id: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Message:
    """Message data model"""
    id: str
    contact_id: str
    contact_name: str
    type: str
    original: str
    result: Optional[str]
    sentiment: Optional[str]
    emotional_state: Optional[str]
    model: Optional[str]
    healing_score: Optional[int]
    user_id: str
    created_at: datetime


@dataclass
class AIResponse:
    """AI response data model"""
    transformed_message: str
    healing_score: int
    sentiment: str
    emotional_state: str
    explanation: str
    subtext: str = ""
    needs: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    model_used: str = ""  # User-friendly model name (e.g., "DeepSeek Chat v3")
    model_id: str = ""    # Technical model ID (e.g., "deepseek/deepseek-chat-v3-0324:free")
    
    def __post_init__(self):
        if self.needs is None:
            self.needs = []
        if self.warnings is None:
            self.warnings = []

    @property
    def model_display(self) -> str:
        """Get display-friendly model information"""
        if self.model_used:
            return f"Powered by {self.model_used}"
        elif self.model_id:
            # Fallback to cleaning up the model_id if no friendly name
            clean_name = self.model_id.split("/")[-1].replace(":free", "").replace("-", " ").title()
            return f"Powered by {clean_name}"
        else:
            return "AI-generated response"

    @property
    def is_fallback_response(self) -> bool:
        """Check if this response came from the fallback system"""
        return self.model_id == "fallback" or self.model_used == "Fallback System"

    def get_model_info(self) -> dict:
        """Get complete model information as dictionary"""
        return {
            "friendly_name": self.model_used,
            "technical_id": self.model_id,
            "display_text": self.model_display,
            "is_fallback": self.is_fallback_response
        }
