"""
Custom exceptions for The Third Voice AI
Provides structured error handling throughout the application
"""

from typing import Optional, List, Dict, Any
from fastapi import status


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        error_type: str = "application_error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        self.field = field
        self.errors = errors or []
        super().__init__(
            message=message,
            error_type="validation_error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class AuthenticationException(AppException):
    """Authentication related exceptions"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_type="authentication_error",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(AppException):
    """Authorization related exceptions"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_type="authorization_error", 
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundException(AppException):
    """Resource not found exceptions"""
    
    def __init__(self, message: str, resource_type: str = "resource"):
        super().__init__(
            message=message,
            error_type="not_found_error",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type}
        )


class ConflictException(AppException):
    """Resource conflict exceptions"""
    
    def __init__(self, message: str, conflicting_resource: Optional[str] = None):
        details = {}
        if conflicting_resource:
            details["conflicting_resource"] = conflicting_resource
            
        super().__init__(
            message=message,
            error_type="conflict_error",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitException(AppException):
    """Rate limiting exceptions"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            error_type="rate_limit_error",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class DatabaseException(AppException):
    """Database related exceptions"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
            
        super().__init__(
            message=message,
            error_type="database_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class AIServiceException(AppException):
    """AI service related exceptions"""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        details = {}
        if model_name:
            details["model_name"] = model_name
        if error_code:
            details["error_code"] = error_code
            
        super().__init__(
            message=message,
            error_type="ai_service_error",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class ConfigurationException(AppException):
    """Configuration related exceptions"""
    
    def __init__(self, message: str, setting_name: Optional[str] = None):
        details = {}
        if setting_name:
            details["setting_name"] = setting_name
            
        super().__init__(
            message=message,
            error_type="configuration_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class DemoLimitException(AppException):
    """Demo user limit exceptions"""
    
    def __init__(
        self,
        message: str,
        limit_type: str,
        current_count: int,
        max_allowed: int
    ):
        super().__init__(
            message=message,
            error_type="demo_limit_error",
            status_code=status.HTTP_403_FORBIDDEN,
            details={
                "limit_type": limit_type,
                "current_count": current_count,
                "max_allowed": max_allowed
            }
        )


class FileUploadException(AppException):
    """File upload related exceptions"""
    
    def __init__(
        self,
        message: str,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        max_size: Optional[int] = None
    ):
        details = {}
        if file_name:
            details["file_name"] = file_name
        if file_size and max_size:
            details["file_size"] = file_size
            details["max_size"] = max_size
            
        super().__init__(
            message=message,
            error_type="file_upload_error",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details=details
        )


# Specific exceptions for business logic
class ContactNotFoundException(NotFoundException):
    """Contact not found exception"""
    
    def __init__(self, contact_id: str):
        super().__init__(
            message=f"Contact with ID '{contact_id}' not found",
            resource_type="contact"
        )


class MessageNotFoundException(NotFoundException):
    """Message not found exception"""
    
    def __init__(self, message_id: str):
        super().__init__(
            message=f"Message with ID '{message_id}' not found",
            resource_type="message"
        )


class UserNotFoundException(NotFoundException):
    """User not found exception"""
    
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User '{identifier}' not found",
            resource_type="user"
        )


class InvalidTokenException(AuthenticationException):
    """Invalid JWT token exception"""
    
    def __init__(self, reason: str = "Invalid token"):
        super().__init__(f"Invalid token: {reason}")


class ExpiredTokenException(AuthenticationException):
    """Expired JWT token exception"""
    
    def __init__(self):
        super().__init__("Token has expired")


class ContactLimitReachedException(ConflictException):
    """Contact limit reached exception"""
    
    def __init__(self, current_count: int, max_allowed: int):
        super().__init__(
            f"Maximum number of contacts ({max_allowed}) reached. Current: {current_count}"
        )


class MessageLimitReachedException(ConflictException):
    """Message limit reached exception"""
    
    def __init__(self, current_count: int, max_allowed: int):
        super().__init__(
            f"Maximum number of messages ({max_allowed}) reached. Current: {current_count}"
        )


class AIModelUnavailableException(AIServiceException):
    """AI model unavailable exception"""
    
    def __init__(self, model_name: str):
        super().__init__(
            message=f"AI model '{model_name}' is currently unavailable",
            model_name=model_name
        )


class InvalidContextException(ValidationException):
    """Invalid context type exception"""
    
    def __init__(self, context: str, valid_contexts: List[str]):
        super().__init__(
            message=f"Invalid context '{context}'. Valid contexts: {', '.join(valid_contexts)}",
            field="context"
        )


class EmptyMessageException(ValidationException):
    """Empty message content exception"""
    
    def __init__(self):
        super().__init__(
            message="Message content cannot be empty",
            field="original"
        )


class MessageTooLongException(ValidationException):
    """Message too long exception"""
    
    def __init__(self, length: int, max_length: int):
        super().__init__(
            message=f"Message too long ({length} chars). Maximum: {max_length} chars",
            field="original"
        )


# Exception helpers
def raise_for_demo_limit(
    current_count: int,
    max_allowed: int,
    limit_type: str,
    item_name: str
):
    """Helper to raise demo limit exceptions"""
    if current_count >= max_allowed:
        raise DemoLimitException(
            message=f"Demo accounts are limited to {max_allowed} {item_name}s. "
                   f"Upgrade to a full account for unlimited access.",
            limit_type=limit_type,
            current_count=current_count,
            max_allowed=max_allowed
        )


def handle_database_error(error: Exception, operation: str) -> None:
    """Helper to convert database errors to application exceptions"""
    error_msg = str(error)
    
    if "UNIQUE constraint failed" in error_msg:
        raise ConflictException(f"Duplicate entry during {operation}")
    elif "FOREIGN KEY constraint failed" in error_msg:
        raise ValidationException(f"Invalid reference during {operation}")
    elif "NOT NULL constraint failed" in error_msg:
        raise ValidationException(f"Missing required field during {operation}")
    else:
        raise DatabaseException(f"Database error during {operation}: {error_msg}", operation)


def validate_message_content(content: str, max_length: int = 5000) -> None:
    """Validate message content and raise appropriate exceptions"""
    if not content or not content.strip():
        raise EmptyMessageException()
    
    if len(content) > max_length:
        raise MessageTooLongException(len(content), max_length)


def validate_contact_name(name: str) -> None:
    """Validate contact name and raise appropriate exceptions"""
    if not name or not name.strip():
        raise ValidationException("Contact name cannot be empty", field="name")
    
    if len(name.strip()) > 100:
        raise ValidationException("Contact name too long (max 100 chars)", field="name")


# Export all exceptions
__all__ = [
    # Base exceptions
    "AppException",
    "ValidationException",
    "AuthenticationException", 
    "AuthorizationException",
    "NotFoundException",
    "ConflictException",
    "RateLimitException",
    "DatabaseException",
    "AIServiceException",
    "ConfigurationException",
    "DemoLimitException",
    "FileUploadException",
    # Specific exceptions
    "ContactNotFoundException",
    "MessageNotFoundException", 
    "UserNotFoundException",
    "InvalidTokenException",
    "ExpiredTokenException",
    "ContactLimitReachedException",
    "MessageLimitReachedException",
    "AIModelUnavailableException",
    "InvalidContextException",
    "EmptyMessageException",
    "MessageTooLongException",
    # Helper functions
    "raise_for_demo_limit",
    "handle_database_error",
    "validate_message_content",
    "validate_contact_name"
]
    "
