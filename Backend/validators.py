"""Input validation utilities."""
import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    if len(email) > 254:
        return False, "Email is too long"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Check for common typos
    common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    domain = email.split('@')[1] if '@' in email else ''
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    # Check for at least one letter and one number (optional but recommended)
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter or not has_number:
        return True, "Warning: Password should contain both letters and numbers"
    
    return True, ""

def validate_text_input(text: str, min_length: int = 10, max_length: int = 10000) -> Tuple[bool, str]:
    """
    Validate text input for prediction.
    
    Args:
        text: Text to validate
        min_length: Minimum text length
        max_length: Maximum text length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Text is required"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Text too short (minimum {min_length} characters)"
    
    if len(text) > max_length:
        return False, f"Text too long (maximum {max_length} characters)"
    
    # Check if text contains actual content (not just special characters)
    alphanumeric_count = sum(c.isalnum() for c in text)
    if alphanumeric_count < min_length / 2:
        return False, "Text must contain meaningful content"
    
    return True, ""

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit consecutive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
