"""
Messages API routes for The Third Voice AI
AI-powered message processing and conversation management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Dict, Any, Optional
import logging

from ...auth.auth_manager import get_current_user
from ...data.schemas import (
    MessageCreate, 
    MessageResponse, 
    AIResponse,
    UserResponse,
    MessageType,
    SentimentType
)
from ...data.database import get_database_manager, DatabaseManager
from ...ai.ai_engine import ai_engine
from ...core.exceptions import (
    ContactNotFoundException,
    MessageNotFoundException,
    DemoLimitException,
    ValidationException,
    AIServiceException,
    raise_for_demo_limit,
    validate_message_content
)
from ...core.config import settings

# Setup
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.post("/process", response_model=MessageResponse)
@limiter.limit("30/minute")
async def process_message(
    request: Request,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> MessageResponse:
    """
    Process a message with AI transformation or interpretation
    
    - TRANSFORM: Rewrites message to be more constructive
    - INTERPRET: Explains what someone really means and suggests responses
    """
    try:
        logger.info(f"Processing message for user: {current_user.email}")
        
        # Validate message content
        validate_message_content(message_data.original)
        
        # Check demo limits
        if db._is_demo_user(current_user.id):
            user_messages = []
            contacts = await db.get_user_contacts(current_user.id)
            for contact in contacts:
                messages = await db.get_conversation_history(contact.id, current_user.id, limit=1000)
                user_messages.extend(messages)
            
            raise_for_demo_limit(
                len(user_messages),
                settings.DEMO_MAX_MESSAGES,
                "messages", 
                "message"
            )
        
        # Verify contact exists
        contact = await db.get_contact_by_id(message_data.contact_id, current_user.id)
        if not contact:
            raise ContactNotFoundException(message_data.contact_id)
        
        # Check cache first
        message_hash = db.create_message_hash(message_data.original, contact.context.value)
        cached_response = await db.check_cache(
            message_data.contact_id, 
            message_hash, 
            current_user.id
        )
        
        if cached_response:
            logger.info("⚡ Using cached AI response")
            ai_response = cached_response
        else:
            # Process with AI
            logger.info(f"🤖 Processing message with AI: {message_data.type.value}")
            ai_response = await ai_engine.process_message(
                message=message_data.original,
                contact_context=contact.context.value,
                message_type=message_data.type.value,
                contact_id=message_data.contact_id,
                user_id=current_user.id
            )
            
            # Cache response in background
            background_tasks.add_task(
                _cache_ai_response,
                db,
                message_data.contact_id,
                message_hash,
                contact.context.value,
                current_user.id,
                ai_response
            )
        
        # Save message to database
        saved_message = await db.save_message(message_data, current_user.id, ai_response)
        
        if not saved_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save processed message"
            )
        
        logger.info(f"✅ Message processed successfully for {current_user.email}")
        return saved_message
        
    except ValidationException:
        raise
    except DemoLimitException:
        raise
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing message for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process message"
        )


@router.get("/", response_model=List[MessageResponse])
@limiter.limit("30/minute")
async def get_messages(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager),
    contact_id: Optional[str] = None,
    limit: int = 50
) -> List[MessageResponse]:
    """
    Get messages for current user
    
    Optionally filter by contact_id to get conversation history
    """
    try:
        logger.info(f"Fetching messages for user: {current_user.email}")
        
        if contact_id:
            # Get messages for specific contact
            contact = await db.get_contact_by_id(contact_id, current_user.id)
            if not contact:
                raise ContactNotFoundException(contact_id)
            
            messages = await db.get_conversation_history(contact_id, current_user.id, limit)
            logger.info(f"✅ Retrieved {len(messages)} messages for contact {contact_id}")
            
        else:
            # Get all user messages across contacts
            all_messages = []
            contacts = await db.get_user_contacts(current_user.id)
            
            for contact in contacts:
                contact_messages = await db.get_conversation_history(contact.id, current_user.id, limit)
                all_messages.extend(contact_messages)
            
            # Sort by creation date and limit
            all_messages.sort(key=lambda x: x.created_at, reverse=True)
            messages = all_messages[:limit]
            
            logger.info(f"✅ Retrieved {len(messages)} total messages for {current_user.email}")
        
        return messages
        
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching messages for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch messages"
        )


@router.get("/{message_id}", response_model=MessageResponse)
@limiter.limit("30/minute")
async def get_message(
    request: Request,
    message_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> MessageResponse:
    """
    Get a specific message by ID
    """
    try:
        logger.info(f"Fetching message {message_id} for user: {current_user.email}")
        
        # For simplicity, we'll search through all contacts
        # In a production system, you might have a direct message lookup
        contacts = await db.get_user_contacts(current_user.id)
        
        for contact in contacts:
            messages = await db.get_conversation_history(contact.id, current_user.id, limit=1000)
            for message in messages:
                if message.id == message_id:
                    logger.info(f"✅ Found message {message_id}")
                    return message
        
        logger.warning(f"❌ Message {message_id} not found for user {current_user.email}")
        raise MessageNotFoundException(message_id)
        
    except MessageNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching message {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch message"
        )


@router.post("/batch", response_model=List[MessageResponse])
@limiter.limit("10/minute")
async def process_batch_messages(
    request: Request,
    messages_data: List[MessageCreate],
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> List[MessageResponse]:
    """
    Process multiple messages in batch
    
    Limited to prevent abuse and resource exhaustion
    """
    try:
        logger.info(f"Processing batch of {len(messages_data)} messages for user: {current_user.email}")
        
        # Limit batch size
        if len(messages_data) > 5:
            raise ValidationException("Batch size limited to 5 messages")
        
        # Check demo limits
        if db._is_demo_user(current_user.id):
            user_messages = []
            contacts = await db.get_user_contacts(current_user.id)
            for contact in contacts:
                messages = await db.get_conversation_history(contact.id, current_user.id, limit=1000)
                user_messages.extend(messages)
            
            raise_for_demo_limit(
                len(user_messages) + len(messages_data),
                settings.DEMO_MAX_MESSAGES,
                "messages",
                "message"
            )
        
        processed_messages = []
        
        for message_data in messages_data:
            try:
                # Validate each message
                validate_message_content(message_data.original)
                
                # Verify contact exists
                contact = await db.get_contact_by_id(message_data.contact_id, current_user.id)
                if not contact:
                    raise ContactNotFoundException(message_data.contact_id)
                
                # Process with AI
                ai_response = await ai_engine.process_message(
                    message=message_data.original,
                    contact_context=contact.context.value,
                    message_type=message_data.type.value,
                    contact_id=message_data.contact_id,
                    user_id=current_user.id
                )
                
                # Save message
                saved_message = await db.save_message(message_data, current_user.id, ai_response)
                if saved_message:
                    processed_messages.append(saved_message)
                
                # Cache response in background
                message_hash = db.create_message_hash(message_data.original, contact.context.value)
                background_tasks.add_task(
                    _cache_ai_response,
                    db,
                    message_data.contact_id,
                    message_hash,
                    contact.context.value,
                    current_user.id,
                    ai_response
                )
                
            except Exception as e:
                logger.error(f"❌ Failed to process message in batch: {str(e)}")
                continue
        
        logger.info(f"✅ Processed {len(processed_messages)} messages in batch")
        return processed_messages
        
    except ValidationException:
        raise
    except DemoLimitException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing batch messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process message batch"
        )


@router.get("/stats/user")
@limiter.limit("20/minute")
async def get_user_message_stats(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager),
    days: int = 30
) -> Dict[str, Any]:
    """
    Get message statistics for current user
    """
    try:
        logger.info(f"Fetching message stats for user: {current_user.email}")
        
        stats = await db.get_message_stats(current_user.id, days)
        
        logger.info(f"✅ Generated message stats for {current_user.email}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error generating message stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate message statistics"
        )


@router.post("/quick-transform")
@limiter.limit("50/minute")
async def quick_transform(
    request: Request,
    message: str,
    contact_context: str = "friend",
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Quick message transformation without saving to database
    
    Useful for testing or one-off transformations
    """
    try:
        logger.info(f"Quick transform request from user: {current_user.email}")
        
        # Validate message
        validate_message_content(message)
        
        # Process with AI (no caching for quick transforms)
        ai_response = await ai_engine.process_message(
            message=message,
            contact_context=contact_context,
            message_type=MessageType.TRANSFORM.value,
            contact_id="quick-transform",
            user_id=current_user.id
        )
        
        result = {
            "original": message,
            "transformed": ai_response.transformed_message,
            "healing_score": ai_response.healing_score,
            "sentiment": ai_response.sentiment.value,
            "emotional_state": ai_response.emotional_state,
            "explanation": ai_response.explanation,
            "model_used": ai_response.model_used,
            "context": contact_context
        }
        
        logger.info(f"✅ Quick transform completed for {current_user.email}")
        return result
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in quick transform: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not transform message"
        )


@router.post("/quick-interpret")
@limiter.limit("50/minute")
async def quick_interpret(
    request: Request,
    message: str,
    contact_context: str = "friend",
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Quick message interpretation without saving to database
    """
    try:
        logger.info(f"Quick interpret request from user: {current_user.email}")
        
        # Validate message
        validate_message_content(message)
        
        # Process with AI
        ai_response = await ai_engine.process_message(
            message=message,
            contact_context=contact_context,
            message_type=MessageType.INTERPRET.value,
            contact_id="quick-interpret",
            user_id=current_user.id
        )
        
        result = {
            "original": message,
            "suggested_response": ai_response.transformed_message,
            "interpretation": ai_response.explanation,
            "subtext": ai_response.subtext,
            "emotional_needs": ai_response.needs,
            "warnings": ai_response.warnings,
            "healing_score": ai_response.healing_score,
            "sentiment": ai_response.sentiment.value,
            "emotional_state": ai_response.emotional_state,
            "model_used": ai_response.model_used,
            "context": contact_context
        }
        
        logger.info(f"✅ Quick interpret completed for {current_user.email}")
        return result
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in quick interpret: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not interpret message"
        )


# Background task for caching AI responses
async def _cache_ai_response(
    db: DatabaseManager,
    contact_id: str,
    message_hash: str,
    context: str,
    user_id: str,
    ai_response: AIResponse
):
    """Background task to cache AI response"""
    try:
        await db.save_to_cache(
            contact_id=contact_id,
            message_hash=message_hash,
            context=context,
            user_id=user_id,
            ai_response=ai_response
        )
        logger.info(f"✅ Cached AI response for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to cache AI response: {str(e)}")


@router.delete("/cache/clear")
@limiter.limit("5/minute")
async def clear_user_cache(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    Clear AI response cache for current user
    """
    try:
        logger.info(f"Clearing cache for user: {current_user.email}")
        
        cleared_count = await db.clean_expired_cache(current_user.id)
        
        logger.info(f"✅ Cleared {cleared_count} cache entries for {current_user.email}")
        return {
            "message": f"Cleared {cleared_count} cached responses",
            "user_id": current_user.id,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not clear cache"
        )
