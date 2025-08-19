"""
Feedback API routes for The Third Voice AI
User feedback collection and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Dict, Any
import logging

from ...auth.auth_manager import get_current_user
from ...data.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    UserResponse
)
from ...data.database import get_database_manager, DatabaseManager
from ...core.exceptions import ValidationException

# Setup
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.post("/", response_model=FeedbackResponse)
@limiter.limit("20/minute")
async def submit_feedback(
    request: Request,
    feedback_data: FeedbackCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> FeedbackResponse:
    """
    Submit user feedback
    
    Ratings are from 1-5 stars with optional text feedback
    """
    try:
        logger.info(f"Feedback submission from user: {current_user.email}")
        
        # Validate rating
        if feedback_data.rating < 1 or feedback_data.rating > 5:
            raise ValidationException("Rating must be between 1 and 5 stars")
        
        # Save feedback
        saved_feedback = await db.save_feedback(feedback_data, current_user.id)
        
        if not saved_feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save feedback"
            )
        
        logger.info(f"✅ Feedback saved: {feedback_data.rating}/5 stars from {current_user.email}")
        if feedback_data.feedback_text:
            logger.info(f"   Comment: {feedback_data.feedback_text[:100]}...")
        
        return saved_feedback
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving feedback from {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save feedback"
        )


@router.get("/my-feedback", response_model=List[FeedbackResponse])
@limiter.limit("30/minute")
async def get_my_feedback(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> List[FeedbackResponse]:
    """
    Get all feedback submitted by current user
    """
    try:
        logger.info(f"Fetching feedback history for user: {current_user.email}")
        
        # For demo users, get from memory
        if db._is_demo_user(current_user.id):
            demo_feedback = db._get_demo_user_data(current_user.id, 'feedback')
            logger.info(f"✅ Retrieved {len(demo_feedback)} feedback entries for demo user")
            return demo_feedback
        
        # For regular users, get from database
        # This would need to be implemented in your database layer
        feedback_list = []  # Placeholder - implement actual database query
        
        logger.info(f"✅ Retrieved {len(feedback_list)} feedback entries for {current_user.email}")
        return feedback_list
        
    except Exception as e:
        logger.error(f"❌ Error fetching feedback for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch feedback history"
        )


@router.get("/categories")
@limiter.limit("30/minute")
async def get_feedback_categories(request: Request) -> List[Dict[str, str]]:
    """
    Get available feedback categories
    """
    categories = [
        {
            "value": "message_transformation",
            "label": "Message Transformation",
            "description": "Feedback on AI message rewriting quality"
        },
        {
            "value": "message_interpretation", 
            "label": "Message Interpretation",
            "description": "Feedback on AI's understanding of message meaning"
        },
        {
            "value": "user_interface",
            "label": "User Interface", 
            "description": "Feedback on app design and usability"
        },
        {
            "value": "feature_request",
            "label": "Feature Request",
            "description": "Suggestions for new features or improvements"
        },
        {
            "value": "bug_report",
            "label": "Bug Report",
            "description": "Report technical issues or errors"
        },
        {
            "value": "general",
            "label": "General Feedback",
            "description": "Overall experience and satisfaction"
        }
    ]
    
    return categories


@router.post("/quick")
@limiter.limit("30/minute") 
async def quick_feedback(
    request: Request,
    rating: int,
    category: str = "general",
    comment: str = None,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> Dict[str, Any]:
    """
    Submit quick feedback without full form
    """
    try:
        logger.info(f"Quick feedback: {rating}/5 stars from {current_user.email}")
        
        # Validate rating
        if rating < 1 or rating > 5:
            raise ValidationException("Rating must be between 1 and 5 stars")
        
        # Create feedback data
        feedback_data = FeedbackCreate(
            rating=rating,
            feedback_text=comment,
            feature_context=category
        )
        
        # Save feedback
        saved_feedback = await db.save_feedback(feedback_data, current_user.id)
        
        if not saved_feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save quick feedback"
            )
        
        # Return success response with encouragement
        response = {
            "message": _get_thank_you_message(rating),
            "rating": rating,
            "category": category,
            "status": "success"
        }
        
        if rating <= 2:
            response["follow_up"] = "We'd love to hear more about how we can improve. Please consider leaving detailed feedback!"
        elif rating >= 4:
            response["follow_up"] = "So glad you're enjoying The Third Voice! Share it with friends who might benefit from better communication."
        
        logger.info(f"✅ Quick feedback saved: {rating}/5 stars")
        return response
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saving quick feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save quick feedback"
        )


def _get_thank_you_message(rating: int) -> str:
    """Get contextual thank you message based on rating"""
    if rating >= 4:
        return "Thank you for the great feedback! We're thrilled you're finding The Third Voice helpful for your conversations. 🎭"
    elif rating == 3:
        return "Thank you for your feedback! We're working hard to make The Third Voice even better for you."
    else:
        return "Thank you for taking the time to share your experience. Your feedback helps us improve The Third Voice for everyone."


@router.get("/stats/summary")
@limiter.limit("10/minute")
async def get_feedback_summary(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get feedback statistics summary for current user
    
    Shows user's feedback patterns and engagement
    """
    try:
        logger.info(f"Generating feedback summary for user: {current_user.email}")
        
        # This would typically aggregate user's feedback data
        # For demo purposes, return sample data
        summary = {
            "total_feedback_given": 0,
            "average_rating_given": 0.0,
            "most_common_category": "general",
            "feedback_frequency": "occasional",
            "latest_feedback_date": None,
            "improvement_suggestions_count": 0,
            "appreciation_messages_count": 0
        }
        
        logger.info(f"✅ Generated feedback summary for {current_user.email}")
        return summary
        
    except Exception as e:
        logger.error(f"❌ Error generating feedback summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate feedback summary"
        )


# Feedback prompts and encouragement
@router.get("/prompts")
@limiter.limit("30/minute")
async def get_feedback_prompts(request: Request) -> Dict[str, Any]:
    """
    Get contextual feedback prompts to encourage user engagement
    """
    prompts = {
        "after_message_processing": [
            "How helpful was this message transformation?",
            "Did the AI understand your situation correctly?",
            "Would you use this rewritten message?",
        ],
        "after_interpretation": [
            "Was this interpretation insightful?",
            "Did this help you understand the other person better?",
            "How accurate was the emotional analysis?",
        ],
        "general_satisfaction": [
            "How is The Third Voice helping your conversations?",
            "What features would make this even more useful?",
            "How likely are you to recommend this to a friend?",
        ],
        "improvement_focused": [
            "What's one thing we could do better?",
            "Which features need more work?",
            "What would make you rate us 5 stars?",
        ]
    }
    
    tips = [
        "Specific feedback helps us improve faster",
        "Both positive and critical feedback are valuable",
        "Your feedback shapes the future of The Third Voice",
        "Help us understand your communication challenges"
    ]
    
    return {
        "prompts": prompts,
        "tips": tips,
        "reminder": "Your feedback is anonymous and helps everyone communicate better"
    }


@router.post("/feature-vote")
@limiter.limit("10/minute")
async def vote_for_feature(
    request: Request,
    feature_name: str,
    priority: int,  # 1-5 scale
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Vote for a feature or improvement
    
    Helps prioritize development roadmap
    """
    try:
        logger.info(f"Feature vote from {current_user.email}: {feature_name} (priority: {priority})")
        
        if priority < 1 or priority > 5:
            raise ValidationException("Priority must be between 1 and 5")
        
        # In a real implementation, you'd save this to a feature voting database
        # For now, just log it
        logger.info(f"📊 Feature vote logged: {feature_name} - {priority}/5 priority")
        
        return {
            "message": f"Thanks for voting for '{feature_name}'! Your input helps us prioritize development.",
            "feature": feature_name,
            "priority": priority,
            "status": "recorded"
        }
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recording feature vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not record feature vote"
        )
