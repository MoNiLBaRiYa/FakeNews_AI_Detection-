"""Unit tests for FND module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.FND import clean_text, predict_news, fetch_and_predict_news

def test_clean_text_basic():
    """Test basic text cleaning."""
    text = "This is a TEST!"
    result = clean_text(text)
    assert result == "this is a test"

def test_clean_text_urls():
    """Test URL removal."""
    text = "Check this https://example.com news"
    result = clean_text(text)
    assert "https" not in result
    assert "example.com" not in result

def test_clean_text_html():
    """Test HTML tag removal."""
    text = "<p>This is <b>bold</b> text</p>"
    result = clean_text(text)
    assert "<p>" not in result
    assert "<b>" not in result

def test_clean_text_special_chars():
    """Test special character removal."""
    text = "Hello! @#$ World?"
    result = clean_text(text)
    assert "@" not in result
    assert "#" not in result
    assert "$" not in result

def test_clean_text_empty():
    """Test empty text handling."""
    result = clean_text("")
    assert result == ""

def test_clean_text_none():
    """Test None handling."""
    result = clean_text(None)
    assert result == ""

def test_clean_text_multiple_spaces():
    """Test multiple spaces handling."""
    text = "This    has    multiple    spaces"
    result = clean_text(text)
    assert "    " not in result
    assert result == "this has multiple spaces"

def test_clean_text_mixed_case():
    """Test mixed case handling."""
    text = "ThIs Is MiXeD CaSe"
    result = clean_text(text)
    assert result == "this is mixed case"

def test_predict_news_empty():
    """Test prediction with empty text."""
    result = predict_news("")
    assert result == "Unknown"

def test_predict_news_valid():
    """Test prediction with valid text."""
    text = "This is a test news article about politics and elections."
    result = predict_news(text)
    assert result in ["Fake News", "Real News", "Unknown", "Error"]

def test_fetch_and_predict_news():
    """Test fetching and predicting news."""
    result = fetch_and_predict_news("test")
    assert isinstance(result, dict)
    assert 'news' in result
    assert 'predictions' in result
    assert isinstance(result['news'], list)
    assert isinstance(result['predictions'], list)

def test_clean_text_with_numbers():
    """Test text with numbers."""
    text = "News 123 about 456 events"
    result = clean_text(text)
    # Numbers should be removed
    assert "123" not in result
    assert "456" not in result

def test_clean_text_with_www():
    """Test www URL removal."""
    text = "Visit www.example.com for more"
    result = clean_text(text)
    assert "www" not in result
    assert "example" not in result
