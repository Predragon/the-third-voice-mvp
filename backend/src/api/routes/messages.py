"""
Messages API routes for The Third Voice AI
AI-powered message processing and conversation management
Authentication removed for MVP simplicity
"""

from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from ...data.schemas import (
    MessageType,
    SentimentType
)
from ...ai.ai_engine import ai_engine, AnalysisDepth
from ...core.exceptions import (
    ValidationException,
    AIServiceException,
    validate_message_content
)
from ...core.config import settings
from pydantic import BaseModel

# Setup
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

# Pydantic model for JSON body
class QuickMessageRequest(BaseModel):
    message: str
    contact_context: str = "friend"
    contact_name: str = "Friend"
    use_deep_analysis: bool = False
    mode: Optional[str] = None

@router.post("/quick-transform")
@limiter.limit("50/minute")
async def quick_transform(
    request: Request,
    message_data: QuickMessageRequest
) -> Dict[str, Any]:
    """
    Quick message transformation without authentication
    
    Transforms messages to be more constructive and healing
    """
    try:
        logger.info(f"Quick transform request: {message_data.message[:50]}... (Deep analysis: {message_data.use_deep_analysis})")
        
        # Validate message
        validate_message_content(message_data.message)
        
        # Determine analysis depth
        analysis_depth = AnalysisDepth.DEEP if message_data.use_deep_analysis else AnalysisDepth.QUICK
        
        # Process with AI
        ai_response = await ai_engine.process_message(
            message=message_data.message,
            contact_context=message_data.contact_context,
            message_type=MessageType.TRANSFORM.value,
            contact_id="anonymous",
            user_id="anonymous",
            analysis_depth=analysis_depth
        )
        
        result = {
            "original": message_data.message,
            "transformed_message": ai_response.transformed_message,
            "healing_score": ai_response.healing_score or 8,
            "sentiment": ai_response.sentiment,
            "emotional_state": ai_response.emotional_state,
            "explanation": ai_response.explanation,
            "model_used": ai_response.model_used,
            "context": message_data.contact_context,
            "analysis_depth": "deep" if message_data.use_deep_analysis else "quick"
        }
        
        logger.info(f"Transform completed successfully")
        return result
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error in quick transform: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not transform message"
        )

@router.post("/quick-interpret")
@limiter.limit("50/minute")
async def quick_interpret(
    request: Request,
    message_data: QuickMessageRequest
) -> Dict[str, Any]:
    """
    Quick message interpretation without authentication
    
    Helps understand what someone really means and suggests responses
    """
    try:
        logger.info(f"Quick interpret request: {message_data.message[:50]}... (Deep analysis: {message_data.use_deep_analysis})")
        
        # Validate message
        validate_message_content(message_data.message)
        
        # Determine analysis depth
        analysis_depth = AnalysisDepth.DEEP if message_data.use_deep_analysis else AnalysisDepth.QUICK
        
        # Process with AI
        ai_response = await ai_engine.process_message(
            message=message_data.message,
            contact_context=message_data.contact_context,
            message_type=MessageType.INTERPRET.value,
            contact_id="anonymous",
            user_id="anonymous",
            analysis_depth=analysis_depth
        )
        
        # Generate suggested responses (what the user should send back)
        suggested_responses = []
        
        # Try to get responses from AI first - but NOT from explanation field
        if hasattr(ai_response, 'suggested_responses') and ai_response.suggested_responses:
            if isinstance(ai_response.suggested_responses, list):
                suggested_responses = [resp for resp in ai_response.suggested_responses if resp and resp.strip() and not resp.startswith("They are")]
            elif isinstance(ai_response.suggested_responses, str) and not ai_response.suggested_responses.startswith("They are"):
                suggested_responses = [ai_response.suggested_responses]
        
        # If AI didn't provide proper response suggestions, generate contextual ones
        if not suggested_responses:
            if message_data.contact_context in ['coparenting', 'co-parent']:
                suggested_responses = [
                    "I can see this has been frustrating for you. You're right that we both need to be more engaged. How can we set up a better system?",
                    "I hear that you're feeling unsupported, and I want to change that. Our kids deserve better from both of us. What would help?",
                    "You're absolutely right to call this out. I need to be more reliable and communicative. Can we talk about what that looks like?"
                ]
            elif message_data.contact_context in ['partner', 'spouse']:
                suggested_responses = [
                    "I can see how frustrated this has made you, and I understand why. Your feelings are completely valid.",
                    "You're right to bring this up. I haven't been as supportive as I should be. How can we work on this together?",
                    "I hear that you're feeling neglected, and that's not okay. What do you need from me to feel more supported?"
                ]
            else:
                suggested_responses = [
                    "I can see this has been really frustrating for you. Your feelings are completely valid.",
                    "Thank you for sharing this with me. I want to understand better - can you help me see what would be most helpful?",
                    "I hear what you're saying, and I want to work together to make this better."
                ]
        
        
        # Ensure we have a proper explanation/interpretation
        interpretation = ""
        if hasattr(ai_response, 'explanation') and ai_response.explanation and ai_response.explanation.strip():
            interpretation = ai_response.explanation
        else:
            # Generate interpretation based on available data
            emotional_context = ""
            if ai_response.emotional_state:
                emotional_context = f"feeling {ai_response.emotional_state}"
            elif ai_response.sentiment and ai_response.sentiment != "neutral":
                emotional_context = f"{ai_response.sentiment}"
            
            if message_data.contact_context in ['coparenting', 'co-parent']:
                interpretation = f"This message reflects concerns about parenting partnership and communication. The sender is expressing {emotional_context} about coordination and shared responsibilities in raising your children together."
            elif message_data.contact_context in ['partner', 'spouse']:
                interpretation = f"This message indicates relationship concerns where the sender is {emotional_context} about feeling supported and heard in your partnership."
            else:
                interpretation = f"The sender is communicating {emotional_context} and seeking better understanding and connection in your relationship."
            
            # Add context about communication patterns if available
            if ai_response.subtext:
                interpretation += f" The deeper need appears to be: {ai_response.subtext.lower()}"
        
        result = {
            "original": message_data.message,
            "interpretation": interpretation,
            "explanation": interpretation,  # Ensure both fields are populated
            "suggested_response": suggested_responses[0] if suggested_responses else "",
            "suggested_responses": suggested_responses,
            "subtext": ai_response.subtext,
            "emotional_needs": ai_response.needs,
            "warnings": ai_response.warnings,
            "healing_score": ai_response.healing_score or 8,
            "sentiment": ai_response.sentiment,
            "emotional_state": ai_response.emotional_state,
            "model_used": ai_response.model_used,
            "context": message_data.contact_context,
            "analysis_depth": "deep" if message_data.use_deep_analysis else "quick"
        }
        
        logger.info(f"Interpret completed successfully")
        return result
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error in quick interpret: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not interpret message"
        )

@router.get("/health")
async def messages_health():
    """Simple health check for messages service"""
    return {
        "status": "healthy",
        "service": "messages",
        "ai_models_available": len(ai_engine.models),
        "timestamp": datetime.now()
    }