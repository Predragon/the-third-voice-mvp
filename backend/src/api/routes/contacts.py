"""
Contacts API routes for The Third Voice AI
CRUD operations for managing conversation contacts
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Optional
import logging

from ...auth.auth_manager import get_current_user
from ...data.schemas import (
    ContactCreate, 
    ContactUpdate, 
    ContactResponse, 
    UserResponse,
    ContextType
)
from ...data.database import get_database_manager, DatabaseManager
from ...core.exceptions import (
    ContactNotFoundException,
    DemoLimitException,
    ValidationException,
    raise_for_demo_limit,
    validate_contact_name
)
from ...core.config import settings

# Setup
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[ContactResponse])
@limiter.limit("30/minute")
async def get_contacts(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> List[ContactResponse]:
    """
    Get all contacts for the current user
    
    Returns list of contacts ordered by most recently updated
    """
    try:
        logger.info(f"Fetching contacts for user: {current_user.email}")
        
        contacts = await db.get_user_contacts(current_user.id)
        
        logger.info(f"✅ Retrieved {len(contacts)} contacts for {current_user.email}")
        return contacts
        
    except Exception as e:
        logger.error(f"❌ Error fetching contacts for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch contacts"
        )


@router.post("/", response_model=ContactResponse)
@limiter.limit("20/minute")
async def create_contact(
    request: Request,
    contact_data: ContactCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> ContactResponse:
    """
    Create a new contact
    
    Demo users are limited to a maximum number of contacts
    """
    try:
        logger.info(f"Creating contact '{contact_data.name}' for user: {current_user.email}")
        
        # Validate contact data
        validate_contact_name(contact_data.name)
        
        # Check demo limits
        if db._is_demo_user(current_user.id):
            current_contacts = await db.get_user_contacts(current_user.id)
            raise_for_demo_limit(
                len(current_contacts),
                settings.DEMO_MAX_CONTACTS,
                "contacts",
                "contact"
            )
        
        # Create contact
        contact = await db.create_contact(contact_data, current_user.id)
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create contact"
            )
        
        logger.info(f"✅ Created contact '{contact.name}' (ID: {contact.id}) for {current_user.email}")
        return contact
        
    except ValidationException:
        raise
    except DemoLimitException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating contact for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create contact"
        )


@router.get("/{contact_id}", response_model=ContactResponse)
@limiter.limit("30/minute")
async def get_contact(
    request: Request,
    contact_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> ContactResponse:
    """
    Get a specific contact by ID
    """
    try:
        logger.info(f"Fetching contact {contact_id} for user: {current_user.email}")
        
        contact = await db.get_contact_by_id(contact_id, current_user.id)
        
        if not contact:
            logger.warning(f"❌ Contact {contact_id} not found for user {current_user.email}")
            raise ContactNotFoundException(contact_id)
        
        logger.info(f"✅ Retrieved contact '{contact.name}' for {current_user.email}")
        return contact
        
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching contact {contact_id} for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch contact"
        )


@router.put("/{contact_id}", response_model=ContactResponse)
@limiter.limit("20/minute")
async def update_contact(
    request: Request,
    contact_id: str,
    contact_update: ContactUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
) -> ContactResponse:
    """
    Update a contact's information
    """
    try:
        logger.info(f"Updating contact {contact_id} for user: {current_user.email}")
        
        # Validate updated name if provided
        if contact_update.name is not None:
            validate_contact_name(contact_update.name)
        
        # Check if contact exists first
        existing_contact = await db.get_contact_by_id(contact_id, current_user.id)
        if not existing_contact:
            raise ContactNotFoundException(contact_id)
        
        # Update contact
        updated_contact = await db.update_contact(contact_id, contact_update, current_user.id)
        
        if not updated_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update contact"
            )
        
        logger.info(f"✅ Updated contact '{updated_contact.name}' for {current_user.email}")
        return updated_contact
        
    except ValidationException:
        raise
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating contact {contact_id} for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update contact"
        )


@router.delete("/{contact_id}")
@limiter.limit("10/minute")
async def delete_contact(
    request: Request,
    contact_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    Delete a contact and all associated messages
    
    This action cannot be undone
    """
    try:
        logger.info(f"Deleting contact {contact_id} for user: {current_user.email}")
        
        # Check if contact exists first
        existing_contact = await db.get_contact_by_id(contact_id, current_user.id)
        if not existing_contact:
            raise ContactNotFoundException(contact_id)
        
        # Delete contact
        success = await db.delete_contact(contact_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete contact"
            )
        
        logger.info(f"✅ Deleted contact '{existing_contact.name}' for {current_user.email}")
        return {
            "message": f"Contact '{existing_contact.name}' deleted successfully",
            "deleted_contact_id": contact_id,
            "status": "success"
        }
        
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting contact {contact_id} for {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete contact"
        )


@router.get("/{contact_id}/messages")
@limiter.limit("30/minute") 
async def get_contact_messages(
    request: Request,
    contact_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return")
):
    """
    Get conversation history for a specific contact
    """
    try:
        logger.info(f"Fetching messages for contact {contact_id}, user: {current_user.email}")
        
        # Check if contact exists first
        contact = await db.get_contact_by_id(contact_id, current_user.id)
        if not contact:
            raise ContactNotFoundException(contact_id)
        
        # Get messages
        messages = await db.get_conversation_history(contact_id, current_user.id, limit)
        
        logger.info(f"✅ Retrieved {len(messages)} messages for contact {contact_id}")
        return {
            "contact": contact,
            "messages": messages,
            "total_messages": len(messages),
            "limit_applied": limit
        }
        
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching messages for contact {contact_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch conversation history"
        )


@router.get("/contexts/available", response_model=List[dict])
@limiter.limit("30/minute")
async def get_available_contexts(request: Request):
    """
    Get list of available context types for contacts
    """
    contexts = [
        {
            "value": context.value,
            "label": context.value.title(),
            "description": _get_context_description(context)
        }
        for context in ContextType
    ]
    
    return contexts


def _get_context_description(context: ContextType) -> str:
    """Get user-friendly description for context types"""
    descriptions = {
        ContextType.ROMANTIC: "Romantic partner or dating relationship",
        ContextType.COPARENTING: "Co-parenting with ex-partner", 
        ContextType.WORKPLACE: "Work colleagues or professional contacts",
        ContextType.FAMILY: "Family members and relatives",
        ContextType.FRIEND: "Friends and social connections"
    }
    return descriptions.get(context, "General communication context")


@router.get("/{contact_id}/stats")
@limiter.limit("20/minute")
async def get_contact_stats(
    request: Request,
    contact_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseManager = Depends(get_database_manager)
):
    """
    Get statistics for a specific contact
    """
    try:
        logger.info(f"Fetching stats for contact {contact_id}, user: {current_user.email}")
        
        # Check if contact exists
        contact = await db.get_contact_by_id(contact_id, current_user.id)
        if not contact:
            raise ContactNotFoundException(contact_id)
        
        # Get conversation history
        messages = await db.get_conversation_history(contact_id, current_user.id, limit=1000)
        
        # Calculate stats
        total_messages = len(messages)
        transform_messages = len([m for m in messages if m.type.value == "transform"])
        interpret_messages = len([m for m in messages if m.type.value == "interpret"])
        
        healing_scores = [m.healing_score for m in messages if m.healing_score is not None]
        avg_healing_score = sum(healing_scores) / len(healing_scores) if healing_scores else 0.0
        
        # Sentiment breakdown
        sentiment_counts = {}
        for message in messages:
            if message.sentiment:
                sentiment = message.sentiment.value
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Recent activity
        recent_messages = [m for m in messages[:10]]  # Last 10 messages
        
        stats = {
            "contact": contact,
            "total_messages": total_messages,
            "transform_count": transform_messages,
            "interpret_count": interpret_messages,
            "avg_healing_score": round(avg_healing_score, 2),
            "sentiment_breakdown": sentiment_counts,
            "messages_with_scores": len(healing_scores),
            "recent_activity": recent_messages,
            "last_message_date": messages[0].created_at if messages else None
        }
        
        logger.info(f"✅ Generated stats for contact {contact_id}")
        return stats
        
    except ContactNotFoundException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating stats for contact {contact_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate contact statistics"
        )
