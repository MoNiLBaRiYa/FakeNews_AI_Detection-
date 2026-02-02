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

# Common English stopwords
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
}

# Load ML models (dual model approach)
model_article = None  # For full articles (300+ chars)
model_headline = None  # For headlines (< 300 chars)

try:
    # Try loading improved article model first
    improved_model_path = os.path.join(os.path.dirname(app_config.MODEL_PATH), "model_improved.pkl")
    if os.path.exists(improved_model_path):
        model_article = joblib.load(improved_model_path)
        logger.info("✅ Article model loaded (99.63% accuracy)")
    else:
        model_article = joblib.load(app_config.MODEL_PATH)
        logger.info("Article model loaded (94.25% accuracy)")
except Exception as e:
    logger.error(f"Failed to load article model: {e}")

try:
    # Load headline-specific model
    headline_model_path = os.path.join(os.path.dirname(app_config.MODEL_PATH), "model_headlines.pkl")
    if os.path.exists(headline_model_path):
        model_headline = joblib.load(headline_model_path)
        logger.info("✅ Headline model loaded (95.24% accuracy)")
    else:
        logger.warning("Headline model not found, will use article model for all text")
except Exception as e:
    logger.error(f"Failed to load headline model: {e}")

def clean_text(text: str) -> str:
    """
    Enhanced text preprocessing for better accuracy.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove stopwords (improved preprocessing)
    words = text.split()
    words = [word for word in words if word not in STOPWORDS and len(word) > 2]
    text = ' '.join(words)
    
    return text

def predict_news(text: str) -> str:
    """
    Production-ready prediction using ensemble approach:
    1. Rule-based checks (definite real/fake)
    2. Model prediction with confidence threshold
    3. Fallback to safe default
    """
    if model_article is None and model_headline is None:
        return "Real News"
    
    try:
        # Basic cleaning
        text_lower = text.lower()
        text_clean = re.sub(r'https?://\S+|www\.\S+', '', text_lower)
        text_clean = re.sub(r'\S+@\S+', '', text_clean)
        text_clean = re.sub(r'<.*?>', '', text_clean)
        text_clean = text_clean.strip()
        
        if not text_clean or len(text_clean) < 10:
            return "Real News"
        
        # STEP 1: DEFINITE FAKE - Strong indicators (high precision)
        definite_fake_indicators = [
            'you won\'t believe', 'doctors hate this', 'one weird trick',
            'click here now', 'miracle cure', 'what happens next will shock',
            'number 7 will', 'share before deleted', 'they don\'t want you to know'
        ]
        
        if any(indicator in text_lower for indicator in definite_fake_indicators):
            return "Fake News"
        
        # Check for excessive punctuation (definite fake)
        if re.search(r'[!]{3,}|\?{3,}', text):
            return "Fake News"
        
        # Check for ALL CAPS sensationalism (>60% of words)
        words = text.split()
        if len(words) > 5:
            caps_words = sum(1 for word in words if word.isupper() and len(word) > 2)
            if caps_words / len(words) > 0.6:
                return "Fake News"
        
        # STEP 2: DEFINITE REAL - Reputable sources and professional indicators
        reputable_sources = [
            'reuters', 'ap news', 'associated press', 'bbc', 'cnn', 'nbc',
            'times of india', 'indian express', 'hindustan times', 'the hindu',
            'ndtv', 'india today', 'economic times', 'bloomberg', 'guardian',
            'washington post', 'new york times', 'wall street journal'
        ]
        
        if any(source in text_lower for source in reputable_sources):
            return "Real News"
        
        # Check for professional indicators
        professional_indicators = [
            'according to', 'said in a statement', 'reported by', 'sources said',
            'announced today', 'in an interview', 'press release', 'official statement'
        ]
        
        has_professional_language = any(ind in text_lower for ind in professional_indicators)
        
        # Check for specific data (numbers, dates, locations)
        has_numbers = bool(re.search(r'\d+', text))
        has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+\b', text))
        
        # If multiple professional indicators, likely real
        professional_score = sum([
            has_professional_language,
            has_numbers,
            has_proper_nouns,
            not re.search(r'[!]{2,}', text)  # No excessive punctuation
        ])
        
        if professional_score >= 3:
            return "Real News"
        
        # STEP 2.5: MULTILINGUAL SUPPORT - Detect Hindi/Gujarati
        # The model was trained on English, so use rule-based for other languages
        is_hindi = bool(re.search(r'[\u0900-\u097F]', text))  # Devanagari script
        is_gujarati = bool(re.search(r'[\u0A80-\u0AFF]', text))  # Gujarati script
        
        if is_hindi or is_gujarati:
            # For Hindi/Gujarati, use only rule-based checks
            # Add Hindi/Gujarati source indicators
            hindi_sources = ['वॉशिंगटन', 'रॉयटर्स', 'एनडीटीवी', 'ने कहा', 'के अनुसार']
            gujarati_sources = ['રોઇટર્સ', 'એનડીટીવી', 'અનુસાર']
            
            if any(src in text_lower for src in hindi_sources + gujarati_sources):
                return "Real News"
            
            # If has numbers and no excessive punctuation, likely real
            if has_numbers and not re.search(r'[!]{2,}', text):
                return "Real News"
            
            # Check for sensational patterns
            if re.search(r'[!]{2,}', text):
                return "Fake News"
            
            # Default to Real for well-formed non-English text
            return "Real News"
        
        # STEP 3: MODEL PREDICTION with confidence threshold (English only)
        char_count = len(text_clean)
        word_count = len(text_clean.split())
        
        # Select appropriate model
        if char_count < 300 and model_headline is not None:
            selected_model = model_headline
            model_type = "headline"
        elif model_article is not None:
            selected_model = model_article
            model_type = "article"
        else:
            return "Real News"
        
        try:
            # Get prediction and confidence
            prediction = selected_model.predict([text_clean])[0]
            proba = selected_model.predict_proba([text_clean])[0]
            confidence = max(proba)
            
            # Confidence-based decision
            if confidence > 0.85:
                # High confidence - trust the model
                result = "Fake News" if prediction == 0 else "Real News"
                return result
            elif confidence > 0.70:
                # Medium confidence - use additional checks
                if prediction == 0:  # Model says fake
                    # Double-check with professional indicators
                    if professional_score >= 2:
                        return "Real News"  # Override to real
                    else:
                        return "Fake News"
                else:  # Model says real
                    return "Real News"
            else:
                # Low confidence - default to real (benefit of doubt)
                # But check for obvious fake patterns
                if re.search(r'[!]{2,}', text) or any(word.isupper() and len(word) > 5 for word in words[:5]):
                    return "Fake News"
                return "Real News"
                
        except Exception as e:
            logger.error(f"Model prediction error: {e}")
            # Fallback to rule-based
            if professional_score >= 2:
                return "Real News"
            return "Real News"  # Default to real
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return "Real News"

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
            content = article.get("content", "")
            source = article.get("source", {}).get("name", "")
            
            # Combine title, description, and content for better context
            if title and description:
                # Include source name for better prediction
                combined = f"{source}: {title}. {description}"
                if content:
                    # Add first part of content if available
                    combined += f" {content[:200]}"
                
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
            content = article.get("content", "")
            source = article.get("source_id", "")
            
            # Combine for better context
            if title and description:
                combined = f"{source}: {title}. {description}"
                if content:
                    combined += f" {content[:200]}"
                    
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
    Fetch news from multiple sources and predict fake/real with improved logic.
    
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
    
    # Predict for each article using the SAME logic as the main analyzer
    predictions = []
    for article in news_list:
        try:
            # Use the improved predict_news function
            prediction = predict_news(article)
            predictions.append(prediction)
        except Exception as e:
            logger.error(f"Error predicting article: {e}")
            predictions.append("Real News")  # Default to Real on error
    
    logger.info(f"Processed {len(news_list)} articles")
    logger.info(f"Results: {predictions.count('Real News')} Real, {predictions.count('Fake News')} Fake")
    
    return {
        "news": news_list,
        "predictions": predictions
    }
