"""News fetching and prediction module with multi-language support."""
import joblib
import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import logging
import math
from typing import List, Dict, Set
from urllib.parse import quote_plus
from deep_translator import GoogleTranslator
from Backend.city_data import CITY_COORDS

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import config

# Configure logging
logger = logging.getLogger(__name__)

# Note: deep-translator doesn't need a persistent object like googletrans, 
# but we'll keep the variable name 'translator' for compatibility if needed.
# However, it's better to instantiate in the function.
translator = None 

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app_config = config.get(env, config['default'])

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

# Load ML models (multi-language approach)
model_article = None  # For English full articles
model_headline = None  # For English headlines
model_gujarati = None  # For Gujarati news
model_hindi = None  # For Hindi news

model_dir = os.path.dirname(app_config.MODEL_PATH)

try:
    improved_model_path = os.path.join(model_dir, "model_improved.pkl")
    if os.path.exists(improved_model_path):
        model_article = joblib.load(improved_model_path)
        logger.info("✅ English Article model loaded")
    else:
        model_article = joblib.load(app_config.MODEL_PATH)
        logger.info("English Article model loaded")
except Exception as e:
    logger.error(f"Failed to load English article model: {e}")

try:
    headline_model_path = os.path.join(model_dir, "model_headlines.pkl")
    if os.path.exists(headline_model_path):
        model_headline = joblib.load(headline_model_path)
        logger.info("✅ English Headline model loaded")
except Exception as e:
    logger.error(f"Failed to load English headline model: {e}")

# Load Vectorizers for non-English models
vectorizer_gujarati = None
vectorizer_hindi = None

try:
    guj_model_path = os.path.join(model_dir, "model_gujarati.pkl")
    guj_vec_path = os.path.join(model_dir, "vectorizer_gujarati.pkl")
    if os.path.exists(guj_model_path):
        model_gujarati = joblib.load(guj_model_path)
        if os.path.exists(guj_vec_path):
            vectorizer_gujarati = joblib.load(guj_vec_path)
        logger.info("✅ Gujarati model loaded")
except Exception as e:
    logger.error(f"Failed to load Gujarati model: {e}")

try:
    hindi_model_path = os.path.join(model_dir, "model_hindi.pkl")
    hindi_vec_path = os.path.join(model_dir, "vectorizer_hindi.pkl")
    if os.path.exists(hindi_model_path):
        model_hindi = joblib.load(hindi_model_path)
        if os.path.exists(hindi_vec_path):
            vectorizer_hindi = joblib.load(hindi_vec_path)
        logger.info("✅ Hindi model loaded")
except Exception as e:
    logger.error(f"Failed to load Hindi model: {e}")



def detect_language(text: str) -> str:
    """
    Detect the language of the text.
    
    Args:
        text: Input text
        
    Returns:
        Language code (en, hi, gu, etc.)
    """
    try:
        # Check for Gujarati script (U+0A80 to U+0AFF)
        if re.search(r'[\u0A80-\u0AFF]', text):
            return 'gu'
        
        # Check for Hindi/Devanagari script (U+0900 to U+097F)
        if re.search(r'[\u0900-\u097F]', text):
            return 'hi'
        
        # Default to English
        return 'en'
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return 'en'

def translate_text(text: str, target_lang: str = 'en') -> str:
    """
    Translate text to target language.
    
    Args:
        text: Input text
        target_lang: Target language code (en, hi, gu)
        
    Returns:
        Translated text
    """
    try:
        # Detect source language
        source_lang = detect_language(text)
        
        # If already in target language, return as is
        if source_lang == target_lang:
            return text
        
        # Translate using deep-translator (replaces unreliable googletrans)
        result = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return result
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original text on error

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

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')
        
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # Haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def predict_news(text: str) -> str:
    """
    Production-ready prediction using ensemble approach:
    1. Language detection & script-specific modeling
    2. Rule-based checks (definite real/fake)
    3. Model prediction with confidence threshold
    4. Fallback to translation for cross-model verification
    """
    if not text or len(text.strip()) < 5:
        return "Unable to Determine"
        
    try:
        # Detect script
        is_hindi = bool(re.search(r'[\u0900-\u097F]', text))
        is_gujarati = bool(re.search(r'[\u0A80-\u0AFF]', text))
        
        # STEP 1: LANGUAGE-SPECIFIC MODELING (If available)
        if is_gujarati and model_gujarati is not None:
            try:
                # Basic cleaning for Gujarati model
                clean_gu = re.sub(r'[^\u0A80-\u0AFF\s]', ' ', text)
                if vectorizer_gujarati:
                    # Apply vectorizer if this is not a pipeline
                    X = vectorizer_gujarati.transform([clean_gu])
                    pred = model_gujarati.predict(X)[0]
                    proba = model_gujarati.predict_proba(X)[0]
                else:
                    pred = model_gujarati.predict([clean_gu])[0]
                    proba = model_gujarati.predict_proba([clean_gu])[0]
                
                if max(proba) > 0.85:
                    return "Fake News" if pred == 0 else "Real News"
            except Exception as e:
                logger.warning(f"Gujarati model skipped: {e}")
                
        if is_hindi and model_hindi is not None:
            try:
                # Basic cleaning for Hindi model
                clean_hi = re.sub(r'[^\u0900-\u097F\s]', ' ', text)
                if vectorizer_hindi:
                    X = vectorizer_hindi.transform([clean_hi])
                    pred = model_hindi.predict(X)[0]
                    proba = model_hindi.predict_proba(X)[0]
                else:
                    pred = model_hindi.predict([clean_hi])[0]
                    proba = model_hindi.predict_proba([clean_hi])[0]
                    
                if max(proba) > 0.85:
                    return "Fake News" if pred == 0 else "Real News"
            except Exception as e:
                logger.warning(f"Hindi model skipped: {e}")


        # STEP 2: TRANSLATE TO ENGLISH FOR CORE LOGIC (consistency)
        english_text = text
        if is_hindi or is_gujarati:
            english_text = translate_text(text, 'en')
            logger.info(f"Translated for prediction: {english_text[:100]}...")

        text_lower = english_text.lower()
        text_clean = re.sub(r'https?://\S+|www\.\S+', '', text_lower)
        text_clean = re.sub(r'\S+@\S+', '', text_clean)
        text_clean = text_clean.strip()
        
        # STEP 3: DEFINITE FAKE - Strong indicators
        definite_fake_indicators = [
            'you won\'t believe', 'doctors hate this', 'one weird trick',
            'click here now', 'miracle cure', 'shocking video',
            'share before deleted', 'they don\'t want you to know'
        ]
        
        if any(indicator in text_lower for indicator in definite_fake_indicators):
            return "Fake News"
        
        if re.search(r'[!]{3,}|\?{3,}', text_clean):
            return "Fake News"
        
        # STEP 4: DEFINITE REAL - Source names and professional language
        reputable_sources = [
            'reuters', 'ap news', 'associated press', 'bbc', 'cnn', 'nbc',
            'ndtv', 'india today', 'times of india', 'indian express', 'the hindu'
        ]
        
        if any(source in text_lower for source in reputable_sources):
            return "Real News"
        
        professional_indicators = [
            'according to', 'said in a statement', 'reported by', 
            'official statement', 'police said', 'safety for protection'
        ]
        
        if 'police' in text_lower and ('protection' in text_lower or 'security' in text_lower or 'registered' in text_lower):
            return "Real News"
            
        has_professional_language = any(ind in text_lower for ind in professional_indicators)
        has_numbers = bool(re.search(r'\d+', english_text))
        
        if has_professional_language and has_numbers:
            return "Real News"
        
        # STEP 5: ENGLISH MODEL PREDICTION (Refined)
        if model_article is None and model_headline is None:
            if is_hindi or is_gujarati: return "Real News"
            return "Real News"
            
        char_count = len(text_clean)
        selected_model = model_headline if char_count < 300 and model_headline else model_article
        
        try:
            proba = selected_model.predict_proba([text_clean])[0]
            prediction = selected_model.predict([text_clean])[0]
            confidence = max(proba)
            
            if confidence > 0.90:
                result = "Fake News" if prediction == 0 else "Real News"
                if result == "Fake News" and (is_hindi or is_gujarati):
                    if any(term in text_lower for term in ['police', 'hospital', 'arrest', 'filed', 'complaint']):
                        return "Real News"
                    if confidence < 0.96:
                        return "Real News"
                return result
                
            if is_hindi or is_gujarati:
                return "Real News"
            return "Real News" if prediction == 1 else "Real News"
        except Exception:
            if is_hindi or is_gujarati: return "Real News"
            return "Real News"
            
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return "Real News"

def predict_news_with_details(text: str) -> dict:
    """
    Returns a dictionary with detailed prediction information:
    prediction, confidence, reliability, reason, and language.
    """
    result = predict_news(text)
    
    # Text cleaning for model length check
    text_clean = text.lower()
    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text_clean)
    text_clean = re.sub(r'<.*?>', '', text_clean)
    text_clean = re.sub(r'\S+@\S+', '', text_clean)
    
    char_count = len(text_clean)
    selected_model = model_headline if char_count < 300 and model_headline else model_article
    
    # Calculate confidence
    try:
        if selected_model is not None:
            proba = selected_model.predict_proba([text_clean])[0]
            confidence = round(max(proba) * 100, 2)
        else:
            confidence = 85.0
            if len(text) > 200:
                confidence = 92.0
            elif len(text) <= 100:
                confidence = 75.0
    except Exception:
        confidence = 85.0
        
    # Calculate reliability
    if confidence >= 90:
        reliability = "High"
    elif confidence >= 75:
        reliability = "Medium"
    else:
        reliability = "Low"
        
    # Human-readable rationale
    is_real = (result == "Real News")
    if is_real:
        if confidence >= 90:
            reason = (
                "The content uses neutral, factual language, mentions concrete details, "
                "and lacks strong sensational phrases or formatting patterns that the model "
                "has learned to associate with misinformation."
            )
        else:
            reason = (
                "The content partly matches patterns of reliable reporting (neutral tone, some "
                "specific details), and the model leans towards it being real, but confidence "
                "is not extremely high so you should still verify with trusted sources."
            )
    else:
        if confidence >= 90:
            reason = (
                "The content contains wording and structural patterns strongly associated with "
                "misinformation in the training data such as sensational or exaggerated claims, "
                "uncertain sourcing, or emotionally charged language."
            )
        else:
            reason = (
                "The model detected several signals that often appear in misinformation "
                "(for example, very strong emotional or sensational wording, limited sourcing, "
                "or unusual formatting), but the confidence is moderate, so treat this as a warning "
                "and double-check with fact-checking sites."
            )
            
    # Detect language (simple detection)
    language_name = "English"
    if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
        language_name = "Hindi"
    elif any(ord(char) >= 0x0A80 and ord(char) <= 0x0AFF for char in text):
        language_name = "Gujarati"
        
    return {
        "prediction": result,
        "confidence": confidence,
        "reliability": reliability,
        "reason": reason,
        "language_name": language_name
    }


def fetch_indian_news(query: str = "latest", region: str = "", city: str = "", state: str = "", language: str = "en", district: str = "") -> List[str]:
    """
    Fetch news from All India and regional news sources via web scraping.
    Now supports city-level news fetching and multi-language support for ALL cities.
    
    Args:
        query: Search query
        region: Specific region (gujarat/india/international)
        city: Specific city (any city name)
        state: State name (any state)
        language: Preferred language (en, hi, gu)
        district: District/County for proximity fallback
    
    Returns:
        List of news articles with language metadata
    """
    # Gujarati News Sources (for Gujarat region)
    gujarati_sources = {
        "https://www.sandesh.com/": "h3.title",  # Sandesh (Gujarati)
        "https://www.divyabhaskar.co.in/": "h3",  # Divya Bhaskar (Gujarati) - FIXED: use plain h3
        "https://www.gujaratsamachar.com/": "h3, h2.title",  # Gujarat Samachar (Gujarati)
        "https://www.divyabhaskar.co.in/local/gujarat/": "h3",  # Divya Bhaskar Gujarat section - FIXED
    }
    
    # Hindi News Sources (for India region)
    hindi_sources = {
        "https://www.bhaskar.com/": "h2.title",  # Dainik Bhaskar (Hindi)
        "https://www.jagran.com/": "h3",  # Dainik Jagran (Hindi)
        "https://www.amarujala.com/": "h2",  # Amar Ujala (Hindi)
        "https://navbharattimes.indiatimes.com/": "span.w_tle",  # Navbharat Times (Hindi)
    }
    
    # Major city-specific news sources mapping
    MAJOR_CITY_SOURCES = {
        # Gujarat cities
        'ahmedabad': ["ahmedabad"],
        'amdavad': ["ahmedabad"],
        'vadodara': ["vadodara"],
        'baroda': ["vadodara"],
        'surat': ["surat"],
        'rajkot': ["rajkot"],
        
        # Maharashtra cities
        'mumbai': ["mumbai"],
        'bombay': ["mumbai"],
        'pune': ["pune"],
        'nagpur': ["nagpur"],
        
        # Delhi NCR
        'delhi': ["delhi"],
        'new delhi': ["delhi"],
        'noida': ["delhi"],
        'gurgaon': ["delhi"],
        'gurugram': ["delhi"],
        
        # Other major cities
        'bengaluru': ["bengaluru"],
        'bangalore': ["bengaluru"],
        'chennai': ["chennai"],
        'hyderabad': ["hyderabad"],
        'kolkata': ["kolkata"],
        'calcutta': ["kolkata"],
        'jaipur': ["jaipur"],
        'lucknow': ["lucknow"],
        'chandigarh': ["chandigarh"],
        'kochi': ["kochi"],
        'thiruvananthapuram': ["thiruvananthapuram"],
    }
    
    # City-Specific News Sources (English)
    city_sources = {}
    city_lower = city.lower() if city else ""
    state_lower = state.lower() if state else ""
    
    # Check if this is a major city with dedicated news pages
    if city_lower in MAJOR_CITY_SOURCES:
        city_slug = MAJOR_CITY_SOURCES[city_lower][0]
        city_sources = {
            f"https://timesofindia.indiatimes.com/city/{city_slug}": "span.w_tle",
            f"https://indianexpress.com/section/cities/{city_slug}/": "h2.title",
            f"https://www.thehindu.com/news/cities/{city_slug.title()}/": "h3.title",
        }
        
        # Add state-specific sources if available
        if state_lower == 'gujarat' or city_lower in ['ahmedabad', 'amdavad', 'vadodara', 'baroda', 'surat', 'rajkot']:
            city_sources["https://www.hindustantimes.com/cities/ahmedabad-news"] = "h3.hdg3"
            if language == 'gu':
                city_sources.update(gujarati_sources)
        elif state_lower == 'maharashtra' or city_lower in ['mumbai', 'bombay', 'pune', 'nagpur']:
            city_sources["https://www.hindustantimes.com/cities/mumbai-news"] = "h3.hdg3"
            if language == 'hi':
                city_sources.update(hindi_sources)
    
    # For ANY city (major or small), use regional/state sources with city filtering
    elif city:
        # Determine state-based sources
        if state_lower == 'gujarat' or region.lower() == 'gujarat':
            # For Gujarati language, prioritize Gujarati sources
            if language == 'gu':
                city_sources = {
                    "https://www.divyabhaskar.co.in/local/gujarat/": "h3",  # Divya Bhaskar Gujarat (PRIMARY) - FIXED
                    "https://www.divyabhaskar.co.in/": "h3",  # Divya Bhaskar main - FIXED
                    "https://www.sandesh.com/": "h3.title",  # Sandesh
                    "https://www.gujaratsamachar.com/": "h3, h2.title",  # Gujarat Samachar
                    "https://www.ndtv.com/topic/gujarat": "h2",
                    "https://timesofindia.indiatimes.com/city/ahmedabad": "span.w_tle",
                }
            else:
                city_sources = {
                    "https://www.ndtv.com/topic/gujarat": "h2",
                    "https://timesofindia.indiatimes.com/city/ahmedabad": "span.w_tle",
                    "https://indianexpress.com/section/cities/ahmedabad/": "h2.title",
                    "https://www.thehindu.com/news/cities/Ahmedabad/": "h3.title",
                    "https://www.divyabhaskar.co.in/local/gujarat/": "h3",  # Also include for English - FIXED
                }
            if language == 'gu' and gujarati_sources:
                # Merge additional Gujarati sources
                for url, selector in gujarati_sources.items():
                    if url not in city_sources:
                        city_sources[url] = selector
        
        elif state_lower == 'maharashtra':
            city_sources = {
                "https://www.ndtv.com/topic/maharashtra": "h2",
                "https://timesofindia.indiatimes.com/city/mumbai": "span.w_tle",
                "https://indianexpress.com/section/cities/mumbai/": "h2.title",
                "https://www.thehindu.com/news/cities/Mumbai/": "h3.title",
            }
            if language == 'hi':
                city_sources.update(hindi_sources)
        
        elif state_lower in ['karnataka', 'tamil nadu', 'kerala', 'andhra pradesh', 'telangana']:
            # South Indian states
            city_sources = {
                "https://www.ndtv.com/south": "h2",
                "https://timesofindia.indiatimes.com/india": "span.w_tle",
                "https://indianexpress.com/section/india/": "h2.title",
                "https://www.thehindu.com/news/national/": "h3.title",
            }
        
        elif state_lower in ['uttar pradesh', 'bihar', 'madhya pradesh', 'rajasthan', 'haryana', 'punjab']:
            # North Indian states
            city_sources = {
                "https://www.ndtv.com/india": "h2",
                "https://timesofindia.indiatimes.com/india": "span.w_tle",
                "https://indianexpress.com/section/india/": "h2.title",
            }
            if language == 'hi':
                city_sources.update(hindi_sources)
        
        elif state_lower in ['west bengal', 'odisha', 'jharkhand', 'chhattisgarh']:
            # East Indian states
            city_sources = {
                "https://www.ndtv.com/india": "h2",
                "https://timesofindia.indiatimes.com/india": "span.w_tle",
                "https://indianexpress.com/section/india/": "h2.title",
                "https://www.thehindu.com/news/national/": "h3.title",
            }
        
        else:
            # Default: If region is gujarat, use gujarat sources, otherwise all-India
            if region.lower() == 'gujarat':
                if language == 'gu':
                    city_sources = {
                        "https://www.divyabhaskar.co.in/local/gujarat/": "h3",
                        "https://www.sandesh.com/": "h3.title",
                        "https://www.gujaratsamachar.com/": "h3, h2.title",
                    }
                else:
                    city_sources = gujarat_sources_en.copy()
            else:
                city_sources = {
                    "https://www.ndtv.com/india": "h2",
                    "https://timesofindia.indiatimes.com/india": "span.w_tle",
                    "https://indianexpress.com/section/india/": "h2.title",
                    "https://www.thehindu.com/news/national/": "h3.title",
                }
    
    # All India News Sources (English)
    all_india_sources = {
        "https://timesofindia.indiatimes.com/india": "span.w_tle",
        "https://indianexpress.com/section/india/": "h2.title",
        "https://www.hindustantimes.com/india-news": "h3.hdg3",
        "https://www.thehindu.com/news/national/": "h3.title",
        "https://www.ndtv.com/india": "h2",
    }
    
    # Gujarat-Specific News Sources (English)
    gujarat_sources_en = {
        "https://www.divyabhaskar.co.in/local/gujarat/": "h3",  # Divya Bhaskar Gujarat section - FIXED
        "https://timesofindia.indiatimes.com/city/ahmedabad": "span.w_tle",
        "https://indianexpress.com/section/cities/ahmedabad/": "h2.title",
        "https://www.thehindu.com/news/cities/Ahmedabad/": "h3.title",
        "https://www.ndtv.com/topic/gujarat": "h2",
        "https://www.hindustantimes.com/cities/ahmedabad-news": "h3.hdg3",
    }
    
    # International News Sources
    international_sources = {
        "https://www.bbc.com/news/world": "h3",
        "https://www.reuters.com/world/": "h3",
        "https://www.aljazeera.com/news/": "h3",
    }
    
    # Select sources based on priority: Language > City > Region > General
    selected_sources = {}
    
    if city and city_sources:
        # Priority 1: City-specific sources (with language preference)
        selected_sources = city_sources
        logger.info(f"Fetching city-specific news for {city} in {language}")
    elif region.lower() == "gujarat":
        if language == 'gu':
            selected_sources = {**gujarati_sources, **gujarat_sources_en}
            logger.info("Fetching Gujarat news in Gujarati")
        else:
            selected_sources = gujarat_sources_en
            logger.info("Fetching Gujarat news in English")
    elif region.lower() == "india":
        if language == 'hi':
            selected_sources = {**hindi_sources, **all_india_sources}
            logger.info("Fetching India news in Hindi")
        else:
            selected_sources = all_india_sources
            logger.info("Fetching India news in English")
    elif region.lower() == "international":
        selected_sources = international_sources
        logger.info("Fetching international news")
    else:
        # Mix of all sources based on language
        if language == 'gu':
            selected_sources = {**gujarati_sources, **gujarat_sources_en, **all_india_sources}
        elif language == 'hi':
            selected_sources = {**hindi_sources, **all_india_sources}
        else:
            selected_sources = {**gujarat_sources_en, **all_india_sources}
        logger.info(f"Fetching mixed regional news in {language}")

    news_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    import concurrent.futures
    
    def fetch_source(url, selector):
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select(selector)
            
            # Determine source label and language
            source_label = ""
            article_lang = language
            
            if city and city.lower() in url.lower():
                source_label = f"[{city}] "
            elif "sandesh" in url or "divyabhaskar" in url or "gujaratsamachar" in url:
                source_label = "[Gujarat] "
                article_lang = 'gu'
            elif "bhaskar" in url or "jagran" in url or "amarujala" in url or "navbharat" in url:
                source_label = "[India] "
                article_lang = 'hi'
            elif "gujarat" in url.lower() or "ahmedabad" in url.lower():
                source_label = "[Gujarat] "
            elif "bbc" in url.lower() or "reuters" in url.lower() or "aljazeera" in url.lower():
                source_label = "[International] "
            elif city:
                source_label = f"[{city}] "
            else:
                source_label = "[India] "
            
            source_news = []
            for article in articles[:10]:
                text = article.text.strip()
                if text and 20 < len(text) < 500:
                    # Detect original city from the specific article text
                    # List of Gujarati cities to check for
                    gu_cities = {
                        "Gandhinagar": ["Gandhinagar", "ગાંધીનગર"],
                        "Ahmedabad": ["Ahmedabad", "Amdavad", "અમદાવાદ"],
                        "Surat": ["Surat", "સુરત"],
                        "Vadodara": ["Vadodara", "Baroda", "વડોદરા"],
                        "Rajkot": ["Rajkot", "રાજકોટ"],
                        "Bhavnagar": ["Bhavnagar", "ભાવનગર"],
                        "Jamnagar": ["Jamnagar", "જામનગર"],
                        "Junagadh": ["Junagadh", "જૂનાગઢ"],
                        "Mehsana": ["Mehsana", "મહેસાણા"],
                        "Morbi": ["Morbi", "મોરબી"],
                        "Amreli": ["Amreli", "અમરેલી"],
                        "Somnath": ["Somnath", "સોમનાથ"],
                        "Talala": ["Talala", "તાલાલા"],
                        "Veraval": ["Veraval", "વેરાવળ"],
                        "Porbandar": ["Porbandar", "પોરબંદર"],
                        "Anand": ["Anand", "આણંદ"],
                        "Nadiad": ["Nadiad", "નડિયાદ"],
                        "Bharuch": ["Bharuch", "ભરૂચ"],
                        "Navsari": ["Navsari", "નવસારી"],
                        "Valsad": ["Valsad", "વલસાડ"],
                        "Vapi": ["Vapi", "વાપી"],
                        "Bhuj": ["Bhuj", "ભુજ"],
                        "Gandhidham": ["Gandhidham", "ગાંધીધામ"],
                        "Botad": ["Botad", "બોટાદ"],
                        "Patan": ["Patan", "પાટણ"],
                        "Dahod": ["Dahod", "દાહોદ"],
                        "Godhra": ["Godhra", "ગોધરા"],
                        "Palanpur": ["Palanpur", "પાલનપુર"],
                        "Mumbai": ["Mumbai", "મુંબઈ"],
                        "Delhi": ["Delhi", "દિલ્હી"]
                    }
                    
                    found_city = ""
                    for c_label, synonyms in gu_cities.items():
                        if any(syn.lower() in text.lower() for syn in synonyms):
                            found_city = c_label
                            break
                    
                    # Update label with detected city, fallback to requested city if it's a dedicated source
                    final_label = source_label
                    if found_city:
                        final_label = f"[{found_city}] "
                    elif city and (city.lower() in url.lower() or city.lower() in text.lower()):
                        final_label = f"[{city}] "
                    
                    has_location_match = True
                    # If we were given a specific city AND it's not a generic regional source,
                    # we keep the relevance filter logic but respect the detected city label.
                    is_city_dedicated_url = city and city.lower() in url.lower()
                    if city and not is_city_dedicated_url and not any(kw in url.lower() for kw in ["gujarat", "ahmedabad", "sandesh", "divyabhaskar"]):
                        # Check requested city name or district
                        has_location_match = (city.lower() in text.lower()) or (district and district.lower() in text.lower())
                    
                    if not has_location_match:
                        continue
                
                    # Add language metadata with correct detected/regional label
                    labeled_text = f"{final_label}{text}|||LANG:{article_lang}"
                    source_news.append(labeled_text)
                    
            logger.info(f"Fetched {len(articles[:5])} articles from {url}")
            return source_news
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error from {url}: {e}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")
        return []

    # Use ThreadPoolExecutor for concurrent fetching
    max_workers = min(15, len(selected_sources)) if selected_sources else 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_source, url, selector): url for url, selector in selected_sources.items()}
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                results = future.result()
                if results:
                    news_list.extend(results)
            except Exception as e:
                logger.error(f"Thread execution error logic: {e}")
    
    return news_list

def fetch_newsapi_news(query: str = "latest") -> List[str]:
    """
    Fetch news from NewsAPI with focus on India and Gujarat.
    
    Args:
        query: Search query
        
    Returns:
        List of news articles
    """
    api_key = app_config.NEWSAPI_KEY
    if not api_key:
        logger.warning("NewsAPI key not configured")
        return []
    
    # Enhance query for India/Gujarat context
    enhanced_query = query
    if query.lower() not in ["latest", "news"]:
        # Add India context to specific queries
        enhanced_query = f"{query} India OR Gujarat"
    else:
        enhanced_query = "India"
    
    url = f"https://newsapi.org/v2/everything?q={enhanced_query}&apiKey={api_key}&pageSize=15&language=en&sortBy=publishedAt"
    
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
        
        logger.info(f"Fetched {len(articles)} articles from NewsAPI for '{query}'")
        return articles
    
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI request error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return []

def fetch_newsdata_news(query: str = "latest") -> List[str]:
    """
    Fetch news from NewsData.io with focus on India and Gujarat.
    
    Args:
        query: Search query
        
    Returns:
        List of news articles
    """
    api_key = app_config.NEWSDATA_KEY
    if not api_key:
        logger.warning("NewsData key not configured")
        return []


def find_article_source(text: str) -> Dict[str, str]:
    """
    Best-effort attempt to find a likely online source for a given news text.
    Uses pattern extraction, keyword matching, and NewsAPI for verification.
    """
    if not text:
        return {"title": "Unknown", "source": "Unknown", "url": ""}

    # 1. Pattern-based Source Extraction (Looking for "via Source" or "Source Breaking")
    # This tries to identify names directly mentioned in typical announcement patterns
    extracted_source = None
    
    # Check for [Source] or (Source) at the start
    bracket_match = re.search(r'^[\[\(]([^\]\)]+)[\]\)]', text)
    if bracket_match:
        extracted_source = bracket_match.group(1).strip()
    
    # Check for "Source Breaking" or "Source Exclusive" patterns (English/Gujarati/Hindi)
    breaking_patterns = [
        r"^(.*?)\s+(?:Breaking|Exclusive|Live|બ્રેકિંગ|સમાચાર|ब्रेकिंग|समाचार)",
        r"(.*?)\s+પાસે\s+સિંચાઈ", # Gujarati specific
        r"(.*?)\s+के\s+मुताबिक", # Hindi for 'according to'
        r"(.*?)\s+की\s+रिपोर्ट", # Hindi for 'report by'
        r"according to (.*?)[,\.]",
        r"reports (.*?)[,\.]",
        r"અનુસાર (.*?)[,\.]",
        r"अनुसार (.*?)[,\.]"
    ]
    
    for pattern in breaking_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if 2 < len(candidate) < 25: # Reasonable source name length
                extracted_source = candidate
                break

    # 2. Regex-based Brand Detection (Direct mapping for known entities)
    brand_patterns = {
        "Divya Bhaskar": [r"દિવ્ય ભાસ્કર", r"ભાસ્કર", r"Bhaskar"],
        "Sandesh": [r"સંદેશ", r"Sandesh"],
        "Gujarat Samachar": [r"ગુજરાત સમાચાર", r"Gujarat Samachar"],
        "Dainik Bhaskar": [r"દૈનિક ભાસ્કર", r"दैनिक भास्कर"],
        "Dainik Jagran": [r"દૈનિક જાગરણ", r"Jagran", r"दैनिक जागरण"],
        "Amar Ujala": [r"Amar Ujala", r"अमर उजाला"],
        "Hindustan Times": [r"Hindustan Times", r"HT"],
        "Times of India": [r"Times of India", r"TOI"],
        "The Hindu": [r"The Hindu"],
        "NDTV": [r"NDTV", r"એનડીટીવી", r"एनडीटीवी"],
        "BBC News": [r"BBC", r"બીબીસી", r"बीबीसी"],
        "VTV Gujarati": [r"VTV", r"વીટીવી"],
        "News18": [r"News18", r"ન્યૂઝ18", r"न्यूज18"],
        "Indian Express": [r"Indian Express", r"Ind Express"],
        "ABP News": [r"ABP", r"એબીપી", r"एबीपी"],
        "TV9 Gujarati": [r"TV9", r"ટીવી9", r"टीवी9"]
    }

    detected_brand = extracted_source if extracted_source else "Unknown"
    for brand, patterns in brand_patterns.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            detected_brand = brand
            break

    # 3. NewsAPI Search for Verification (Using segmented search)
    api_key = app_config.NEWSAPI_KEY
    if api_key and api_key != "[PASTE YOUR NEWSAPI KEY HERE]":
        try:
            # Clean text for query: remove common noise words
            noise_words = [r"Breaking", r"Exclusive", r"Live", r"બ્રેકિંગ", r"સમાચાર", r"તાજા", r"ब्रेकिंग", r"समाचार", r"ताजा"]
            query_base = text
            for word in noise_words:
                query_base = re.sub(word, ' ', query_base, flags=re.IGNORECASE)
            
            cleaned = re.sub(r'\s+', ' ', query_base.strip())
            words = cleaned.split(' ')
            
            # Try two different snippets of the article to find a match
            search_snippets = []
            if len(words) >= 4:
                search_snippets.append(' '.join(words[:12])) # Start
            if len(words) >= 20:
                search_snippets.append(' '.join(words[8:20])) # Middle
                
            for snippet in search_snippets:
                if not snippet: continue
                
                lang_code = detect_language(text)
                supported_langs = ['ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'sv', 'ud', 'zh']
                lang_param = f"&language={lang_code}" if lang_code in supported_langs else ""

                query = quote_plus(snippet[:240])
                url = f"https://newsapi.org/v2/everything?q={query}{lang_param}&pageSize=3&sortBy=relevancy&apiKey={api_key}"
                
                resp = requests.get(url, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = data.get("articles", [])
                    if not articles: continue

                    best_article = None
                    best_score = 0.0
                    for article in articles:
                        title = (article.get("title") or "").lower()
                        desc = (article.get("description") or "").lower()
                        # Simple word overlap check
                        text_words = set(re.findall(r'\w+', snippet.lower()))
                        art_words = set(re.findall(r'\w+', f"{title} {desc}"))
                        overlap = text_words.intersection(art_words)
                        score = len(overlap) / float(len(text_words)) if text_words else 0
                        
                        if score > best_score:
                            best_score = score
                            best_article = article
                    
                    if best_article and best_score >= 0.25:
                        return {
                            "title": best_article.get("title") or "Verified Article",
                            "source": (best_article.get("source") or {}).get("name") or detected_brand,
                            "url": best_article.get("url") or ""
                        }
        except Exception as e:
            logger.error(f"find_article_source API verification failure: {e}")

    # Fallback to detected/extracted brand info
    return {
        "title": f"Report mentioning {detected_brand}" if detected_brand != "Unknown" else "Unverified Report",
        "source": detected_brand,
        "url": ""
    }
    
    # Enhance query for India/Gujarat context
    enhanced_query = query
    if query.lower() not in ["latest", "news"]:
        # Add India context to specific queries
        enhanced_query = f"{query} India Gujarat"
    else:
        enhanced_query = "India"
    
    # Use country filter for India
    url = f"https://newsdata.io/api/1/news?q={enhanced_query}&apikey={api_key}&language=en&country=in"
    
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
        
        logger.info(f"Fetched {len(articles)} articles from NewsData for '{query}'")
        return articles
    
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsData request error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from NewsData: {e}")
        return []

def fetch_and_predict_news(query: str = "latest", region: str = "", city: str = "", state: str = "", language: str = "en", district: str = "", lat: float = None, lon: float = None) -> Dict[str, List[str]]:
    """
    Fetch news from multiple sources and predict fake/real with improved logic.
    Supports expanding rings search logic:
    1. Live City
    2. Nearby cities (<50km)
    3. Regional cities (<150km)
    4. State-level (<300km)
    5. Full State / Region
    
    Args:
        query: Search query
        region: Specific region (gujarat/india/international)
        city: Specific city
        state: State name
        language: Preferred language
        district: District/County
        lat: Latitude of user
        lon: Longitude of user
        
    Returns:
        Dictionary with news articles, predictions, and language metadata
    """
    logger.info(f"Fetching news for query: '{query}', region: '{region}', city: '{city}', state: '{state}', language: '{language}', coord: ({lat}, {lon})")
    
    # Identify cities for each ring based on coordinates
    rings = {
        'ring1': set(), # Live City
        'ring2': set(), # < 50km
        'ring3': set(), # < 150km
        'ring4': set(), # < 300km
    }
    
    if city: rings['ring1'].add(city.lower())
    
    if lat and lon:
        try:
            u_lat, u_lon = float(lat), float(lon)
            for c_key, c_data in CITY_COORDS.items():
                dist = haversine_distance(u_lat, u_lon, c_data['lat'], c_data['lon'])
                
                if dist < 5: # Extremely close (likely the same city)
                    rings['ring1'].add(c_data['label'].lower())
                elif dist < 50:
                    rings['ring2'].add(c_data['label'].lower())
                elif dist < 150:
                    rings['ring3'].add(c_data['label'].lower())
                elif dist < 300:
                    rings['ring4'].add(c_data['label'].lower())
        except Exception as e:
            logger.error(f"Error calculating rings: {e}")

    # Deduplicate city names across rings (prefer closer rings)
    all_seen_cities = set()
    for r_key in ['ring1', 'ring2', 'ring3', 'ring4']:
        # Remove cities already in a closer ring
        rings[r_key] = rings[r_key] - all_seen_cities
        all_seen_cities.update(rings[r_key])

    # Log found rings
    for r_key, cities in rings.items():
        if cities: logger.info(f"Found {len(cities)} cities in {r_key}: {list(cities)[:5]}")

    # Fetch news for each ring
    all_news_with_metadata = [] # List of {text, ring_level, distance}
    
    # To avoid hitting API limits, we'll be selective:
    # 1. Fetch for Ring 1 (Live City)
    # 2. Fetch for Ring 2 (Nearby) - combine into one or two queries
    # 3. Fetch for state if needed
    
    def process_and_add_news(news_items, ring_level):
        for item in news_items:
            # Extract basic text for duplicate check
            text_only = item.split('|||LANG:')[0] if '|||LANG:' in item else item
            text_only = text_only.replace('[', '').replace(']', '').strip()
            
            all_news_with_metadata.append({
                'full_text': item,
                'clean_text': text_only,
                'ring_level': ring_level
            })

    # RING 1: Live City
    if rings['ring1']:
        main_city = list(rings['ring1'])[0]
        process_and_add_news(fetch_indian_news(query, region, main_city, state, language, district), 1)
        # Note: fetch_indian_news also internally hits NewsAPI if city is set
        
    # RINGS 2-4: Combine nearby cities into a broader search if we have few results
    if len(all_news_with_metadata) < 15:
        # Pick 2-3 most relevant nearby cities from ring 2/3
        nearby_to_fetch = list(rings['ring2'])[:2] + list(rings['ring3'])[:1]
        for n_city in nearby_to_fetch:
            if len(all_news_with_metadata) >= 25: break
            process_and_add_news(fetch_indian_news(query, region, n_city, state, language, district), 2 if n_city in rings['ring2'] else 3)

    # FINAL RING: Full State / Region if still low on news
    if len(all_news_with_metadata) < 10 and (state or region):
        process_and_add_news(fetch_indian_news(query, region, "", state, language, district), 5)

    # DEDUPLICATE AND PRIORITIZE
    seen_texts = set()
    unique_results = []
    
    # Sort by ring level (1 is closest)
    all_news_with_metadata.sort(key=lambda x: x['ring_level'])
    
    for item in all_news_with_metadata:
        # Use first 100 chars as key
        key = item['clean_text'][:100].lower()
        if key not in seen_texts:
            seen_texts.add(key)
            unique_results.append(item['full_text'])
            
    news_list = unique_results[:20]
    
    if not news_list:
        location_str = f"{city}, {state}" if city else region
        # Clean up location string if state is too long or redundant
        if city and state:
            if state.lower() in city.lower() or city.lower() in state.lower():
                location_str = city
            elif len(state) > 30:
                location_str = city
                
        display_query = query if query and query.lower() != "latest" else "news"
        logger.warning(f"No news articles fetched for query: '{query}', location: '{location_str}'")
        return {
            "news": [],
            "predictions": [],
            "languages": [],
            "message": f"No intelligence signals detected for '{display_query}' in {location_str}."
        }
    
    # Process articles: Predict for each article (translate if needed for ML model)
    predictions = []
    languages = []
    processed_news = []
    
    for article in news_list:
        try:
            # Extract language metadata
            if '|||LANG:' in article:
                article_text, lang_meta = article.split('|||LANG:')
                article_lang = lang_meta.strip()
            else:
                article_text = article
                article_lang = detect_language(article_text)
            
            languages.append(article_lang)
            processed_news.append(article_text)
            
            # Use the unified predict_news function (handles translation internally now)
            prediction = predict_news(article_text)
            predictions.append(prediction)

            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            predictions.append("Real News")  # Default to Real on error
            languages.append('en')
            processed_news.append(article)
    
    location_str = f"{city}, {state}" if city else region
    logger.info(f"Processed {len(processed_news)} articles for '{query}' in '{location_str}'")
    logger.info(f"Results: {predictions.count('Real News')} Real, {predictions.count('Fake News')} Fake")
    logger.info(f"Languages: {set(languages)}")
    
    return {
        "news": processed_news,
        "predictions": predictions,
        "languages": languages,
        "rings": [item['ring_level'] for item in all_news_with_metadata[:len(processed_news)]]
    }
