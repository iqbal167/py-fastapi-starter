"""
Common utility functions for the FastAPI application.
"""
import uuid
import hashlib
import secrets
from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Generate a short random ID.
    
    Args:
        length: Length of the generated ID
        
    Returns:
        Random string of specified length
    """
    return secrets.token_urlsafe(length)[:length]


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of the given data.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def safe_dict_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with nested key support.
    
    Args:
        data: Dictionary to search
        key: Key to search for (supports dot notation for nested keys)
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
        
    Example:
        safe_dict_get({"user": {"name": "John"}}, "user.name") -> "John"
    """
    if "." not in key:
        return data.get(key, default)
    
    keys = key.split(".")
    current = data
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string by removing/replacing problematic characters.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def mask_sensitive_data(data: Union[str, Dict], fields_to_mask: Optional[list] = None) -> Union[str, Dict]:
    """
    Mask sensitive data in strings or dictionaries.
    
    Args:
        data: Data to mask
        fields_to_mask: List of field names to mask (for dict data)
        
    Returns:
        Data with sensitive information masked
    """
    if fields_to_mask is None:
        fields_to_mask = [
            'password', 'token', 'secret', 'key', 'authorization',
            'credit_card', 'ssn', 'social_security', 'api_key'
        ]
    
    if isinstance(data, str):
        # Simple string masking - show first 4 and last 4 characters
        if len(data) <= 8:
            return "*" * len(data)
        return data[:4] + "*" * (len(data) - 8) + data[-4:]
    
    elif isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():
            if any(sensitive_field.lower() in key.lower() for sensitive_field in fields_to_mask):
                if isinstance(value, str) and len(value) > 0:
                    masked_data[key] = mask_sensitive_data(value)
                else:
                    masked_data[key] = "***"
            else:
                masked_data[key] = value
        return masked_data
    
    return data


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human readable format.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1m 30s")
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
