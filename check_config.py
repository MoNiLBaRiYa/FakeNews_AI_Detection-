#!/usr/bin/env python3
"""Diagnostic script to check configuration and API keys."""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and is readable."""
    env_path = Path('.env')
    
    print("=" * 60)
    print("FAKE NEWS DETECTION - Configuration Checker")
    print("=" * 60)
    print()
    
    # Check .env file
    if env_path.exists():
        print(f"✓ .env file found at: {env_path.absolute()}")
        print(f"  File size: {env_path.stat().st_size} bytes")
    else:
        print(f"✗ .env file NOT found at: {env_path.absolute()}")
        print("  Please copy .env.example to .env and add your API keys")
        return False
    
    # Load environment variables
    load_dotenv(dotenv_path=env_path)
    print()
    
    # Check API keys
    print("API Keys Status:")
    print("-" * 60)
    
    newsapi_key = os.getenv('NEWSAPI_KEY', '')
    newsdata_key = os.getenv('NEWSDATA_KEY', '')
    
    # Check NewsAPI key
    if not newsapi_key:
        print("✗ NEWSAPI_KEY: Not set")
    elif newsapi_key == 'your-newsapi-key-here':
        print("⚠ NEWSAPI_KEY: Using placeholder (needs to be replaced)")
    elif len(newsapi_key) < 20:
        print(f"⚠ NEWSAPI_KEY: Too short ({len(newsapi_key)} chars) - might be invalid")
    else:
        print(f"✓ NEWSAPI_KEY: Configured ({len(newsapi_key)} chars)")
        print(f"  Preview: {newsapi_key[:8]}...{newsapi_key[-4:]}")
    
    # Check NewsData key
    if not newsdata_key:
        print("✗ NEWSDATA_KEY: Not set")
    elif newsdata_key == 'your-newsdata-key-here':
        print("⚠ NEWSDATA_KEY: Using placeholder (needs to be replaced)")
    elif len(newsdata_key) < 20:
        print(f"⚠ NEWSDATA_KEY: Too short ({len(newsdata_key)} chars) - might be invalid")
    else:
        print(f"✓ NEWSDATA_KEY: Configured ({len(newsdata_key)} chars)")
        print(f"  Preview: {newsdata_key[:8]}...{newsdata_key[-4:]}")
    
    print()
    
    # Check other important settings
    print("Other Configuration:")
    print("-" * 60)
    print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'development')}")
    print(f"FLASK_DEBUG: {os.getenv('FLASK_DEBUG', 'True')}")
    print(f"MONGODB_URI: {os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27017/')}")
    print(f"DATABASE_NAME: {os.getenv('DATABASE_NAME', 'user_auth_db')}")
    print()
    
    # Check model file
    model_path = Path('Model/model.pkl')
    if model_path.exists():
        print(f"✓ ML Model found at: {model_path.absolute()}")
        print(f"  File size: {model_path.stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"✗ ML Model NOT found at: {model_path.absolute()}")
    
    print()
    print("=" * 60)
    
    # Summary
    has_valid_newsapi = newsapi_key and newsapi_key != 'your-newsapi-key-here' and len(newsapi_key) >= 20
    has_valid_newsdata = newsdata_key and newsdata_key != 'your-newsdata-key-here' and len(newsdata_key) >= 20
    
    if has_valid_newsapi and has_valid_newsdata:
        print("✓ Configuration looks good! You can start the application.")
    elif has_valid_newsapi or has_valid_newsdata:
        print("⚠ Partial configuration. Some news sources may not work.")
    else:
        print("✗ API keys not configured. News fetching will not work.")
        print("\nTo fix:")
        print("1. Get free API keys from:")
        print("   - NewsAPI: https://newsapi.org/register")
        print("   - NewsData: https://newsdata.io/register")
        print("2. Add them to your .env file")
        print("3. Restart the application")
    
    print("=" * 60)
    
    return has_valid_newsapi and has_valid_newsdata

if __name__ == '__main__':
    check_env_file()
