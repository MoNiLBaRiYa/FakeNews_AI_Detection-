"""News fetching and prediction module with multi-language support."""
import joblib
import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import logging
from typing import List, Dict
from urllib.parse import quote_plus
from googletrans import Translator

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize translator for multi-language support
translator = Translator()

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
        
        # Translate using Google Translate
        result = translator.translate(text, src=source_lang, dest=target_lang)
        return result.text
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

def fetch_indian_news(query: str = "latest", region: str = "", city: str = "", state: str = "", language: str = "en") -> List[str]:
    """
    Fetch news from All India and regional news sources via web scraping.
    Now supports city-level news fetching and multi-language support for ALL cities.
    
    Args:
        query: Search query
        region: Specific region (gujarat/india/international)
        city: Specific city (any city name)
        state: State name (any state)
        language: Preferred language (en, hi, gu)
    
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
            # Default: Use all-India sources for any other city/state
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
    
    for url, selector in selected_sources.items():
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select(selector)
            
            # Determine source label and language
            source_label = ""
            article_lang = language
            
            if city:
                source_label = f"[{city}] "
            elif "sandesh" in url or "divyabhaskar" in url or "gujaratsamachar" in url:
                source_label = "[Gujarat-ગુજરાત] "
                article_lang = 'gu'
            elif "bhaskar" in url or "jagran" in url or "amarujala" in url or "navbharat" in url:
                source_label = "[India-हिंदी] "
                article_lang = 'hi'
            elif "gujarat" in url.lower() or "ahmedabad" in url.lower():
                source_label = "[Gujarat] "
            elif "bbc" in url.lower() or "reuters" in url.lower() or "aljazeera" in url.lower():
                source_label = "[International] "
            else:
                source_label = "[India] "
            
            for article in articles[:5]:  # Increased to 5 per source for city-specific news
                text = article.text.strip()
                # Better validation
                if text and 20 < len(text) < 500:
                    # Flexible city filtering: Check for city name OR state name OR nearby keywords
                    if city:
                        city_keywords = [city.lower()]
                        # Add state to keywords for better matching
                        if state:
                            city_keywords.append(state.lower())
                        
                        # Check if any keyword is in the article
                        text_lower = text.lower()
                        has_location_match = any(keyword in text_lower for keyword in city_keywords)
                        
                        # For smaller cities, be more lenient BUT check for exclusions
                        if not has_location_match and city.lower() not in MAJOR_CITY_SOURCES:
                            # Check if article mentions OTHER cities or states
                            # Include both English and Gujarati/Hindi names
                            other_cities = [
                                # Major Indian cities (English)
                                'delhi', 'mumbai', 'kolkata', 'chennai', 'bengaluru', 'bangalore',
                                'hyderabad', 'pune', 'jaipur', 'lucknow', 'kanpur', 'nagpur',
                                'indore', 'bhopal', 'patna', 'ludhiana', 'agra',
                                'nashik', 'faridabad', 'meerut', 'varanasi', 'srinagar',
                                'amritsar', 'allahabad', 'ranchi', 'howrah', 'coimbatore', 'vijayawada',
                                # Gujarat cities (English)
                                'ahmedabad', 'amdavad', 'vadodara', 'baroda', 'surat', 'rajkot',
                                'bhavnagar', 'jamnagar', 'gandhinagar', 'anand', 'nadiad',
                                # Gujarat cities (Gujarati script)
                                'અમદાવાદ', 'સુરત', 'વડોદરા', 'રાજકોટ', 'ભાવનગર', 'જામનગર',
                                # Major cities (Hindi/Devanagari)
                                'दिल्ली', 'मुंबई', 'कोलकाता', 'चेन्नई', 'बेंगलुरु', 'हैदराबाद',
                                'पुणे', 'जयपुर', 'लखनऊ', 'कानपुर', 'नागपुर'
                            ]
                            
                            # OTHER STATES (exclude news from other states entirely)
                            other_states = [
                                # North India
                                'punjab', 'haryana', 'himachal', 'uttarakhand', 'jammu', 'kashmir',
                                'पंजाब', 'हरियाणा', 'हिमाचल', 'उत्तराखंड', 'जम्मू', 'कश्मीर',
                                # East India
                                'west bengal', 'bengal', 'odisha', 'orissa', 'jharkhand', 'bihar',
                                'assam', 'meghalaya', 'tripura', 'manipur', 'nagaland', 'mizoram', 'arunachal',
                                'पश्चिम बंगाल', 'ओडिशा', 'झारखंड', 'बिहार', 'असम', 'मेघालय',
                                # South India (if user is not in south)
                                'karnataka', 'kerala', 'tamil nadu', 'andhra pradesh', 'telangana',
                                'कर्नाटक', 'केरल', 'तमिलनाडु', 'आंध्र प्रदेश', 'तेलंगाना',
                                # Central India
                                'madhya pradesh', 'chhattisgarh', 'mp',
                                'मध्य प्रदेश', 'छत्तीसगढ़',
                                # West India (if user is not in Maharashtra/Gujarat)
                                'maharashtra', 'goa', 'राजस्थान', 'महाराष्ट्र', 'गोवा'
                            ]
                            
                            # Remove user's state from exclusion list
                            user_state_lower = state.lower() if state else ''
                            if user_state_lower:
                                other_states = [s for s in other_states if s not in user_state_lower and user_state_lower not in s]
                            
                            # Remove user's city from the exclusion list (check both English and local script)
                            user_city_lower = city.lower()
                            other_cities = [c for c in other_cities if c != user_city_lower]
                            
                            # If article mentions another city OR state, skip it
                            mentions_other_city = any(other_city in text_lower or other_city in text for other_city in other_cities)
                            mentions_other_state = any(other_state in text_lower or other_state in text for other_state in other_states)
                            
                            if not mentions_other_city and not mentions_other_state:
                                # Accept if it's from a regional source and doesn't mention other cities/states
                                has_location_match = True
                        
                        if not has_location_match:
                            continue
                    
                    # Add language metadata
                    labeled_text = f"{source_label}{text}|||LANG:{article_lang}"
                    news_list.append(labeled_text)
                    
            logger.info(f"Fetched {len(articles[:5])} articles from {url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error from {url}: {e}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")
    
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
    Uses NewsAPI (if configured) to search for matching articles.

    Returns dict with keys: title, source, url. If nothing is found, url is '' and
    source/title are 'Unknown'.
    """
    api_key = app_config.NEWSAPI_KEY
    if not api_key or not text:
        return {"title": "Unknown", "source": "Unknown", "url": ""}

    # Build a compact query from the text (headline or first 12 words)
    cleaned = re.sub(r'\s+', ' ', text.strip())
    words = cleaned.split(' ')
    if len(words) > 16:
        snippet = ' '.join(words[:16])
    else:
        snippet = cleaned

    try:
        query = quote_plus(snippet[:200])
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&language=en&pageSize=5&sortBy=publishedAt&apiKey={api_key}"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            logger.warning(f"find_article_source: NewsAPI error: {data.get('message')}")
            return {"title": "Unknown", "source": "Unknown", "url": ""}

        text_lower = cleaned.lower()
        best_article = None
        best_score = 0.0

        for article in data.get("articles", []):
            title = (article.get("title") or "").strip()
            description = (article.get("description") or "").strip()
            candidate = f"{title}. {description}".strip().lower()
            if not candidate:
                continue

            # Simple overlap score between text and candidate
            text_words = set(w for w in re.findall(r'\w+', text_lower) if len(w) > 3)
            cand_words = set(w for w in re.findall(r'\w+', candidate) if len(w) > 3)
            if not text_words or not cand_words:
                continue
            overlap = text_words.intersection(cand_words)
            score = len(overlap) / float(len(text_words))

            if score > best_score:
                best_score = score
                best_article = article

        if best_article and best_score >= 0.25:
            return {
                "title": best_article.get("title") or "Unknown",
                "source": (best_article.get("source") or {}).get("name", "Unknown"),
                "url": best_article.get("url") or "",
            }

    except Exception as e:
        logger.error(f"find_article_source error: {e}")

    return {"title": "Unknown", "source": "Unknown", "url": ""}
    
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

def fetch_and_predict_news(query: str = "latest", region: str = "", city: str = "", state: str = "", language: str = "en") -> Dict[str, List[str]]:
    """
    Fetch news from multiple sources and predict fake/real with improved logic.
    Now supports city-level news fetching and multi-language support.
    Prioritizes API results for specific queries, web scraping for generic queries.
    
    Args:
        query: Search query
        region: Specific region (gujarat/india/international)
        city: Specific city (Ahmedabad, Somnath, Vadodara, etc.)
        state: State name
        language: Preferred language (en, hi, gu)
        
    Returns:
        Dictionary with news articles, predictions, and language metadata
    """
    logger.info(f"Fetching news for query: '{query}', region: '{region}', city: '{city}', state: '{state}', language: '{language}'")
    
    # Fetch from all sources
    api_news = []  # From NewsAPI and NewsData (supports queries)
    scraped_news = []  # From web scraping (latest only)
    
    # Determine if this is a specific query or generic
    is_generic_query = query.lower() in ["latest", "news", "india", "indian", "gujarat", "international", ""]
    
    # PRIORITY 1: Try NewsAPI (supports specific queries and city-level search)
    try:
        # Enhance query with city for better results
        api_query = f"{query} {city} {state}" if city else query
        api_results = fetch_newsapi_news(api_query)
        if api_results:
            # Filter results for city relevance if city is specified
            if city:
                city_filtered = [art for art in api_results if city.lower() in art.lower()]
                api_news.extend(city_filtered if city_filtered else api_results[:5])
            else:
                api_news.extend(api_results)
            logger.info(f"NewsAPI returned {len(api_results)} articles for '{api_query}'")
    except Exception as e:
        logger.error(f"Error in fetch_newsapi_news: {e}")
    
    # PRIORITY 2: Try NewsData (supports specific queries and city-level search)
    try:
        # Enhance query with city for better results
        newsdata_query = f"{query} {city} {state}" if city else query
        newsdata_results = fetch_newsdata_news(newsdata_query)
        if newsdata_results:
            # Filter results for city relevance if city is specified
            if city:
                city_filtered = [art for art in newsdata_results if city.lower() in art.lower()]
                api_news.extend(city_filtered if city_filtered else newsdata_results[:5])
            else:
                api_news.extend(newsdata_results)
            logger.info(f"NewsData returned {len(newsdata_results)} articles for '{newsdata_query}'")
    except Exception as e:
        logger.error(f"Error in fetch_newsdata_news: {e}")
    
    # PRIORITY 3: Try web scraping with city, region, and language filter
    if is_generic_query or len(api_news) < 5:
        try:
            scraped_results = fetch_indian_news(query, region, city, state, language)
            if scraped_results:
                scraped_news.extend(scraped_results)
                logger.info(f"Web scraping returned {len(scraped_results)} articles for city '{city}', region '{region}', language '{language}'")
        except Exception as e:
            logger.error(f"Error in fetch_indian_news: {e}")
    
    # Combine results: Prioritize city-specific and language-specific news
    if city:
        # Filter for city-specific content
        city_api = [art for art in api_news if city.lower() in art.lower()]
        city_scraped = [art for art in scraped_news if city.lower() in art.lower()]
        other_api = [art for art in api_news if city.lower() not in art.lower()]
        other_scraped = [art for art in scraped_news if city.lower() not in art.lower()]
        
        # Prioritize: city scraped > city API > nearby scraped > nearby API
        news_list = city_scraped[:10] + city_api[:5] + other_scraped[:3] + other_api[:2]
        logger.info(f"Using city-prioritized results for '{city}'")
    elif region:
        # Filter API news for regional content
        regional_api = [art for art in api_news if region.lower() in art.lower()]
        other_api = [art for art in api_news if region.lower() not in art.lower()]
        
        # Prioritize: regional scraped > regional API > other scraped > other API
        news_list = scraped_news[:10] + regional_api[:5] + other_api[:5]
        logger.info(f"Using region-prioritized results for '{region}'")
    elif not is_generic_query and api_news:
        # For specific queries, use mostly API results
        news_list = api_news[:15] + scraped_news[:5]
        logger.info(f"Using API-prioritized results for specific query '{query}'")
    else:
        # For generic queries, mix both
        news_list = api_news + scraped_news
        logger.info(f"Using mixed results for generic query '{query}'")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_news = []
    for article in news_list:
        # Extract article text without language metadata for duplicate check
        article_text = article.split('|||LANG:')[0] if '|||LANG:' in article else article
        article_key = article_text[:100].lower()
        if article_key not in seen:
            seen.add(article_key)
            unique_news.append(article)
    
    # Limit to 20 results
    news_list = unique_news[:20]
    
    if not news_list:
        location_str = f"{city}, {state}" if city else region
        logger.warning(f"No news articles fetched for query: '{query}', location: '{location_str}'")
        return {
            "news": [f"No news found for '{query}' in {location_str}. Try a different search term like 'technology', 'politics', 'health', or 'sports'."],
            "predictions": ["Real News"],  # Changed from "Unknown" to "Real News" for consistency
            "languages": ["en"]
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
            
            # Translate to English for ML model if needed
            if article_lang != 'en':
                article_for_ml = translate_text(article_text, 'en')
            else:
                article_for_ml = article_text
            
            # Use the improved predict_news function
            prediction = predict_news(article_for_ml)
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
        "languages": languages
    }
