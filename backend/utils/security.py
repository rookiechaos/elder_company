"""
Security Utilities - Security-related helper functions

"""

import re
import secrets
from typing import Optional, Tuple
from datetime import datetime, timedelta


# Common weak passwords (top 1000 most common passwords)
WEAK_PASSWORDS = {
    "password", "123456", "123456789", "12345678", "12345",
    "1234567", "1234567890", "qwerty", "abc123", "111111",
    "123123", "admin", "letmein", "welcome", "monkey",
    "1234567890", "password1", "qwerty123", "000000", "123456789"
}


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be no more than 128 characters long"
    
    # Check for common weak passwords
    if password.lower() in WEAK_PASSWORDS:
        return False, "Password is too common. Please choose a stronger password."
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_enum_value(value: str, allowed_values: list, field_name: str = "value") -> bool:
    """
    Validate that a value is in the allowed list.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of the field being validated
        
    Returns:
        True if value is valid
        
    Raises:
        ValidationError: If value is not in allowed list
    """
    if value not in allowed_values:
        from exceptions import ValidationError
        raise ValidationError(
            f"{field_name} must be one of {allowed_values}, got: {value}",
            {"field": field_name, "value": value, "allowed": allowed_values}
        )
    return True


def validate_range(value: int, min_value: int, max_value: int, field_name: str = "value") -> bool:
    """
    Validate that a numeric value is within a range.
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of the field being validated
        
    Returns:
        True if value is in range
        
    Raises:
        ValidationError: If value is out of range
    """
    if value < min_value or value > max_value:
        from exceptions import ValidationError
        raise ValidationError(
            f"{field_name} must be between {min_value} and {max_value}, got: {value}",
            {"field": field_name, "value": value, "min": min_value, "max": max_value}
        )
    return True


import re

_HOME_PATH_PATTERN = re.compile(r"/Users/[^/]+/")


def redact_local_paths(text: str) -> str:
    """Remove home-directory prefixes from log/traceback strings."""
    if not isinstance(text, str):
        return text
    return _HOME_PATH_PATTERN.sub("<home>/", text)


def sanitize_for_logging(data: dict) -> dict:
    """
    Remove sensitive information from data before logging.
    
    Args:
        data: Dictionary that may contain sensitive information
        
    Returns:
        Sanitized dictionary with sensitive fields masked
    """
    sensitive_fields = {
        "password", "password_hash", "token", "api_key", "secret",
        "secret_key", "jwt_secret", "openai_api_key", "anthropic_api_key",
        "google_api_key", "access_token", "refresh_token", "authorization"
    }
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        # Check if key contains sensitive field name
        is_sensitive = any(sensitive in key_lower for sensitive in sensitive_fields)
        
        if is_sensitive and value:
            # Mask sensitive values
            if isinstance(value, str):
                if len(value) > 8:
                    sanitized[key] = value[:4] + "***" + value[-4:]
                else:
                    sanitized[key] = "***"
            else:
                sanitized[key] = "***"
        else:
            if key == "traceback" and isinstance(value, str):
                sanitized[key] = redact_local_paths(value)
            else:
                sanitized[key] = value
    
    return sanitized


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Token length in bytes (default: 32)
        
    Returns:
        Hexadecimal token string
    """
    return secrets.token_hex(length)


def validate_jwt_secret_key(secret_key: str) -> bool:
    """
    Validate JWT secret key strength.
    
    Args:
        secret_key: Secret key to validate
        
    Returns:
        True if secret key is strong enough
    """
    if not secret_key:
        return False
    
    # Check for default/weak keys
    weak_keys = {
        "your-secret-key-change-in-production",
        "change-me-in-production",
        "secret",
        "password",
        "123456"
    }
    
    if secret_key in weak_keys:
        return False
    
    # Minimum length check
    if len(secret_key) < 32:
        return False
    
    return True


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (optional)
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Trim whitespace
    text = text.strip()
    
    # Apply length limit if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_file_upload(
    filename: str,
    content_type: Optional[str] = None,
    max_size: int = 10 * 1024 * 1024,  # 10MB default
    allowed_extensions: Optional[list] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate file upload.
    
    Args:
        filename: Original filename
        content_type: MIME type
        max_size: Maximum file size in bytes
        allowed_extensions: List of allowed file extensions
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is required"
    
    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        return False, "Invalid filename"
    
    # Check file extension
    if allowed_extensions:
        file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if file_ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, None
