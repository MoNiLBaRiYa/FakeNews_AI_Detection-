"""Unit tests for validators module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.validators import (
    validate_email,
    validate_password,
    validate_text_input,
    sanitize_input
)

class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_email(self):
        """Test valid email addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.co.uk',
            'test123@test-domain.com'
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid, f"Email {email} should be valid"
    
    def test_invalid_email(self):
        """Test invalid email addresses."""
        invalid_emails = [
            'invalid',
            '@example.com',
            'test@',
            'test..test@example.com',
            'test@example',
            ''
        ]
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert not is_valid, f"Email {email} should be invalid"
    
    def test_email_too_long(self):
        """Test email that's too long."""
        long_email = 'a' * 250 + '@example.com'
        is_valid, error = validate_email(long_email)
        assert not is_valid

class TestPasswordValidation:
    """Test password validation."""
    
    def test_valid_password(self):
        """Test valid passwords."""
        valid_passwords = [
            'password123',
            'Test1234',
            'MyP@ssw0rd',
            'abcdef123'
        ]
        for password in valid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid, f"Password should be valid"
    
    def test_short_password(self):
        """Test password that's too short."""
        is_valid, error = validate_password('12345')
        assert not is_valid
        assert 'at least 6 characters' in error
    
    def test_empty_password(self):
        """Test empty password."""
        is_valid, error = validate_password('')
        assert not is_valid
    
    def test_long_password(self):
        """Test password that's too long."""
        long_password = 'a' * 200
        is_valid, error = validate_password(long_password)
        assert not is_valid

class TestTextInputValidation:
    """Test text input validation."""
    
    def test_valid_text(self):
        """Test valid text input."""
        text = "This is a valid news article with enough content."
        is_valid, error = validate_text_input(text)
        assert is_valid
    
    def test_short_text(self):
        """Test text that's too short."""
        is_valid, error = validate_text_input("short")
        assert not is_valid
        assert 'too short' in error.lower()
    
    def test_long_text(self):
        """Test text that's too long."""
        long_text = "a" * 15000
        is_valid, error = validate_text_input(long_text)
        assert not is_valid
        assert 'too long' in error.lower()
    
    def test_empty_text(self):
        """Test empty text."""
        is_valid, error = validate_text_input("")
        assert not is_valid
    
    def test_whitespace_only(self):
        """Test text with only whitespace."""
        is_valid, error = validate_text_input("     ")
        assert not is_valid
    
    def test_special_chars_only(self):
        """Test text with only special characters."""
        is_valid, error = validate_text_input("!@#$%^&*()")
        assert not is_valid
        assert 'meaningful content' in error.lower()

class TestSanitizeInput:
    """Test input sanitization."""
    
    def test_normal_text(self):
        """Test normal text sanitization."""
        text = "This is normal text"
        result = sanitize_input(text)
        assert result == text
    
    def test_null_bytes(self):
        """Test null byte removal."""
        text = "Test\x00text"
        result = sanitize_input(text)
        assert '\x00' not in result
    
    def test_multiple_spaces(self):
        """Test multiple spaces normalization."""
        text = "This    has    multiple    spaces"
        result = sanitize_input(text)
        assert "    " not in result
        assert result == "This has multiple spaces"
    
    def test_empty_input(self):
        """Test empty input."""
        result = sanitize_input("")
        assert result == ""
    
    def test_none_input(self):
        """Test None input."""
        result = sanitize_input(None)
        assert result == ""
    
    def test_leading_trailing_spaces(self):
        """Test leading and trailing spaces removal."""
        text = "   text with spaces   "
        result = sanitize_input(text)
        assert result == "text with spaces"
