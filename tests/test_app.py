"""Unit tests for Flask application."""
import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.app import app

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    app.config['RATELIMIT_ENABLED'] = False  # Disable rate limiting for tests
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'model_loaded' in data
    assert 'database_connected' in data

def test_predict_no_text(client):
    """Test prediction with no text."""
    response = client.post('/predict', 
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_predict_short_text(client):
    """Test prediction with short text."""
    response = client.post('/predict', 
                          json={'text': 'short'},
                          content_type='application/json')
    assert response.status_code == 400

def test_predict_valid_text(client):
    """Test prediction with valid text."""
    response = client.post('/predict',
                          json={'text': 'This is a test news article about politics and elections in the country.'},
                          content_type='application/json')
    # Should succeed or fail gracefully
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.get_json()
        assert 'prediction' in data
        assert 'confidence' in data

def test_signup_invalid_email(client):
    """Test signup with invalid email."""
    response = client.post('/signup', 
                          json={'email': 'invalid-email', 'password': 'password123'},
                          content_type='application/json')
    assert response.status_code in [400, 503]

def test_signup_short_password(client):
    """Test signup with short password."""
    response = client.post('/signup',
                          json={'email': 'test@example.com', 'password': '123'},
                          content_type='application/json')
    assert response.status_code in [400, 503]

def test_signup_valid_credentials(client):
    """Test signup with valid credentials."""
    response = client.post('/signup',
                          json={'email': f'test{os.urandom(4).hex()}@example.com', 'password': 'password123'},
                          content_type='application/json')
    # Should succeed or fail if DB unavailable
    assert response.status_code in [201, 400, 503]

def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    response = client.post('/login',
                          json={},
                          content_type='application/json')
    assert response.status_code in [400, 503]

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/login',
                          json={'email': 'nonexistent@example.com', 'password': 'wrongpassword'},
                          content_type='application/json')
    assert response.status_code in [401, 503]

def test_fetch_news_default_query(client):
    """Test news fetching with default query."""
    response = client.get('/fetch_news')
    # Should work with default query or fail gracefully
    assert response.status_code in [200, 404, 500]

def test_fetch_news_custom_query(client):
    """Test news fetching with custom query."""
    response = client.get('/fetch_news?query=technology')
    assert response.status_code in [200, 404, 500]

def test_logout(client):
    """Test logout endpoint."""
    response = client.post('/logout')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data

def test_forgot_password(client):
    """Test forgot password endpoint."""
    response = client.post('/forgot_password',
                          json={'email': 'test@example.com'},
                          content_type='application/json')
    assert response.status_code in [200, 503]

def test_404_error(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_fakenews_page(client):
    """Test fake news detection page."""
    response = client.get('/fakenews')
    assert response.status_code == 200

def test_user_stats_unauthorized(client):
    """Test user stats without authentication."""
    response = client.get('/user/stats')
    assert response.status_code == 401

def test_global_stats(client):
    """Test global statistics endpoint."""
    response = client.get('/global/stats')
    assert response.status_code in [200, 500]

def test_predict_long_text(client):
    """Test prediction with very long text."""
    long_text = "This is a test. " * 1000  # Very long text
    response = client.post('/predict',
                          json={'text': long_text},
                          content_type='application/json')
    assert response.status_code in [200, 400, 503]

def test_predict_special_characters(client):
    """Test prediction with special characters."""
    response = client.post('/predict',
                          json={'text': 'Test news @#$%^&*() with special chars!!! 123456'},
                          content_type='application/json')
    assert response.status_code in [200, 400, 503]
