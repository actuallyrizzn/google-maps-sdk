"""
Utility functions for validation and sanitization
"""

import re
import hashlib
from typing import Optional


# Constants for validation
MIN_API_KEY_LENGTH = 20
API_KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')


def validate_api_key(api_key: str) -> str:
    """
    Validate API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        Stripped API key
        
    Raises:
        TypeError: If API key is not a string
        ValueError: If API key is invalid format
    """
    if not isinstance(api_key, str):
        raise TypeError("API key must be a non-empty string")
    
    if not api_key:
        raise ValueError("API key is required")
    
    api_key = api_key.strip()
    
    if not api_key:
        raise ValueError("API key cannot be whitespace-only")
    
    if len(api_key) < MIN_API_KEY_LENGTH:
        raise ValueError(
            f"API key appears to be invalid (too short: {len(api_key)} chars, "
            f"minimum: {MIN_API_KEY_LENGTH})"
        )
    
    if not API_KEY_PATTERN.match(api_key):
        raise ValueError("API key contains invalid characters (only alphanumeric, underscore, and hyphen allowed)")
    
    return api_key


def sanitize_api_key_for_logging(text: str, api_key: str) -> str:
    """
    Remove API key from log messages to prevent exposure
    
    Args:
        text: Text that may contain API key
        api_key: API key to sanitize
        
    Returns:
        Text with API key replaced by placeholder
    """
    if not api_key or not text:
        return text
    
    # Replace API key with placeholder
    sanitized = re.sub(
        re.escape(api_key),
        "[API_KEY_REDACTED]",
        text,
        flags=re.IGNORECASE
    )
    
    return sanitized


def hash_api_key(api_key: str, length: int = 16) -> str:
    """
    Create a hash of API key for safe logging/display
    
    Args:
        api_key: API key to hash
        length: Length of hash prefix to return
        
    Returns:
        First N characters of SHA256 hash
    """
    if not api_key:
        return ""
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:length]
    return key_hash


def validate_base_url(base_url: str) -> str:
    """
    Validate base URL format
    
    Args:
        base_url: Base URL to validate
        
    Returns:
        Validated and normalized base URL
        
    Raises:
        TypeError: If base_url is not a string
        ValueError: If base_url is invalid format
    """
    if not isinstance(base_url, str):
        raise TypeError("Base URL must be a string")
    
    if not base_url:
        raise ValueError("Base URL is required")
    
    base_url = base_url.strip()
    
    if not base_url:
        raise ValueError("Base URL cannot be whitespace-only")
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'  # domain name
        r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*'  # domain parts
        r'(:[0-9]{1,5})?'  # optional port
        r'(/.*)?$'  # optional path
    )
    
    if not url_pattern.match(base_url):
        raise ValueError(f"Invalid base URL format: {base_url}")
    
    return base_url.rstrip("/")


def validate_timeout(timeout: Optional[int]) -> int:
    """
    Validate timeout value
    
    Args:
        timeout: Timeout value in seconds
        
    Returns:
        Validated timeout value
        
    Raises:
        TypeError: If timeout is not an integer
        ValueError: If timeout is invalid
    """
    if timeout is None:
        return 30  # Default timeout
    
    if not isinstance(timeout, (int, float)):
        raise TypeError("Timeout must be a number")
    
    timeout = int(timeout)
    
    if timeout < 1:
        raise ValueError("Timeout must be at least 1 second")
    
    if timeout > 300:  # 5 minutes max
        raise ValueError("Timeout cannot exceed 300 seconds (5 minutes)")
    
    return timeout


def validate_non_empty_string(value: str, field_name: str = "value") -> str:
    """
    Validate that a string is not empty or whitespace-only
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
        
    Returns:
        Stripped string
        
    Raises:
        TypeError: If value is not a string
        ValueError: If value is empty or whitespace-only
    """
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty or whitespace-only")
    
    return value.strip()
