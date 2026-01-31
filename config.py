"""Configuration management for the Fake News Detection application."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the project root
# This works whether running from root or Backend directory
project_root = Path(__file__).parent
env_path = project_root / '.env'

# If .env not found in current directory, try parent directory
if not env_path.exists():
    env_path = project_root.parent / '.env'

load_dotenv(dotenv_path=env_path)

# Debug: Print if .env was found
if env_path.exists():
    print(f"✓ Loaded .env from: {env_path}")
else:
    print(f"⚠ Warning: .env file not found at {env_path}")

class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'user_auth_db')
    
    # API Keys
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
    NEWSDATA_KEY = os.getenv('NEWSDATA_KEY', '')
    
    # Validate API keys on startup
    @classmethod
    def validate_api_keys(cls):
        """Check if API keys are configured."""
        warnings = []
        if not cls.NEWSAPI_KEY or cls.NEWSAPI_KEY == 'your-newsapi-key-here':
            warnings.append("⚠ NEWSAPI_KEY not configured or using placeholder")
        if not cls.NEWSDATA_KEY or cls.NEWSDATA_KEY == 'your-newsdata-key-here':
            warnings.append("⚠ NEWSDATA_KEY not configured or using placeholder")
        
        if warnings:
            print("\n" + "\n".join(warnings))
            print("News fetching may not work properly. Update your .env file with valid API keys.\n")
        else:
            print("✓ API keys configured successfully\n")
        
        return len(warnings) == 0
    
    # Security
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    
    # Model
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'Model', 'model.pkl')
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
