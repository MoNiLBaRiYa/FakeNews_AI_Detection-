"""News fetching and prediction module."""
import joblib
import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import config

# Configure logging
logger = logging.getLogger(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app_config = config[env]

# Load ML model
model = None
try:
    model = joblib.load(app_config.MODEL_PATH)
    logger.info("Model loaded in FND module")
except Exception as e:
    logger.error(f"Failed to load model in FND: {e}")

def clean_text(text: str) -> str:
    """
    Preprocess text for prediction.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    return text.strip()

def predict_news(text: str) -> str:
    """
    Predict if news is fake or real.
    
    Args:
        text: News article text
        
    Returns:
        Prediction result
    """
    if model is None:
        logger.error("Model not loaded")
        return "Unknown"
    
    try:
        processed_text = clean_text(text)
        if not processed_text:
            return "Unknown"
        
        prediction = model.predict([processed_text])
        return "Fake News" if prediction[0] == 0 else "Real News"
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return "Error"

def fetch_indian_news() -> List[str]:
    """
    Fetch news from Indian news sources via web scraping.
    
    Returns:
        List of news articles
    """
    news_sources = {
        "https://timesofindia.indiatimes.com/india": "span.w_tle",
        "https://indianexpress.com/section/india/": "h2.title",
        "https://www.hindustantimes.com/india-news": "h3.hdg3"
    }

    news_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    for url, selector in news_sources.items():
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select(selector)
            
            for article in articles[:5]:  # Limit to 5 per source
                text = article.text.strip()
                # Better validation
                if text and 20 < len(text) < 500:
                    news_list.append(text)
                    
            logger.info(f"Fetched {len(articles[:5])} articles from {url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error from {url}: {e}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")
    
    return news_list

def fetch_newsapi_news(query: str = "latest") -> List[str]:
    """
    Fetch news from NewsAPI.
    
    Args:
        query: Search query
        
    Returns:
        List of news articles
    """
    api_key = app_config.NEWSAPI_KEY
    if not api_key:
        logger.warning("NewsAPI key not configured")
        return []
    
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=10&language=en&sortBy=publishedAt"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'ok':
            logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return []
        
        articles = []
        for article in data.get("articles", []):
            title = article.get("title", "")
            description = article.get("description", "")
            
            if title and description:
                combined = f"{title}. {description}"
                if len(combined) > 50:  # Ensure meaningful content
                    articles.append(combined)
        
        logger.info(f"Fetched {len(articles)} articles from NewsAPI")
        return articles
    
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI request error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return []

def fetch_newsdata_news(query: str = "latest") -> List[str]:
    """
    Fetch news from NewsData.io.
    
    Args:
        query: Search query
        
    Returns:
        List of news articles
    """
    api_key = app_config.NEWSDATA_KEY
    if not api_key:
        logger.warning("NewsData key not configured")
        return []
    
    url = f"https://newsdata.io/api/1/news?q={query}&apikey={api_key}&language=en&country=in"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'success':
            logger.error(f"NewsData error: {data.get('message', 'Unknown error')}")
            return []
        
        articles = []
        for article in data.get("results", []):
            title = article.get("title", "")
            description = article.get("description", "")
            
            if title and description:
                combined = f"{title}. {description}"
                if len(combined) > 50:
                    articles.append(combined)
        
        logger.info(f"Fetched {len(articles)} articles from NewsData")
        return articles
    
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsData request error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from NewsData: {e}")
        return []

def fetch_and_predict_news(query: str = "latest") -> Dict[str, List[str]]:
    """
    Fetch news from multiple sources and predict fake/real.
    
    Args:
        query: Search query
        
    Returns:
        Dictionary with news articles and predictions
    """
    logger.info(f"Fetching news for query: {query}")
    
    # Fetch from all sources
    news_list = []
    
    # Try web scraping
    try:
        news_list.extend(fetch_indian_news())
    except Exception as e:
        logger.error(f"Error in fetch_indian_news: {e}")
    
    # Try NewsAPI
    try:
        news_list.extend(fetch_newsapi_news(query))
    except Exception as e:
        logger.error(f"Error in fetch_newsapi_news: {e}")
    
    # Try NewsData
    try:
        news_list.extend(fetch_newsdata_news(query))
    except Exception as e:
        logger.error(f"Error in fetch_newsdata_news: {e}")
    
    # Remove duplicates and limit results
    news_list = list(dict.fromkeys(news_list))[:20]
    
    if not news_list:
        logger.warning("No news articles fetched")
        return {
            "news": ["No news found. Please try a different query."],
            "predictions": ["Unknown"]
        }
    
    # Predict for each article
    predictions = []
    for article in news_list:
        try:
            prediction = predict_news(article)
            predictions.append(prediction)
        except Exception as e:
            logger.error(f"Error predicting article: {e}")
            predictions.append("Error")
    
    logger.info(f"Processed {len(news_list)} articles")
    
    return {
        "news": news_list,
        "predictions": predictions
    }
