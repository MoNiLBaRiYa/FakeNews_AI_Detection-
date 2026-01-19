"""Multi-language support for Gujarati and Hindi."""
from googletrans import Translator
from langdetect import detect, LangDetectException
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'gu': 'Gujarati'
}

def detect_language(text: str) -> str:
    """
    Detect the language of input text.
    
    Args:
        text: Input text
        
    Returns:
        Language code (en, hi, gu) or 'en' as default
    """
    try:
        if not text or len(text.strip()) < 3:
            return 'en'
        
        detected = detect(text)
        
        # Map detected language to supported languages
        if detected in SUPPORTED_LANGUAGES:
            return detected
        
        # Default to English
        return 'en'
    
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return 'en'
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return 'en'

def translate_to_english(text: str, source_lang: Optional[str] = None) -> Tuple[str, str]:
    """
    Translate text to English for model prediction.
    
    Args:
        text: Input text in any supported language
        source_lang: Source language code (optional, will auto-detect)
        
    Returns:
        Tuple of (translated_text, detected_language)
    """
    try:
        # Detect language if not provided
        if not source_lang:
            source_lang = detect_language(text)
        
        # If already English, return as is
        if source_lang == 'en':
            return text, 'en'
        
        # Translate to English
        translation = translator.translate(text, src=source_lang, dest='en')
        translated_text = translation.text
        
        logger.info(f"Translated from {source_lang} to English")
        return translated_text, source_lang
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        # Return original text if translation fails
        return text, source_lang or 'en'

def translate_response(text: str, target_lang: str) -> str:
    """
    Translate response back to user's language.
    
    Args:
        text: English text to translate
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    try:
        # If target is English, return as is
        if target_lang == 'en':
            return text
        
        # Translate to target language
        translation = translator.translate(text, src='en', dest=target_lang)
        return translation.text
    
    except Exception as e:
        logger.error(f"Response translation error: {e}")
        # Return original text if translation fails
        return text

def get_language_name(lang_code: str) -> str:
    """
    Get language name from code.
    
    Args:
        lang_code: Language code (en, hi, gu)
        
    Returns:
        Language name
    """
    return SUPPORTED_LANGUAGES.get(lang_code, 'English')

def is_supported_language(lang_code: str) -> bool:
    """
    Check if language is supported.
    
    Args:
        lang_code: Language code
        
    Returns:
        True if supported, False otherwise
    """
    return lang_code in SUPPORTED_LANGUAGES

# Predefined translations for common responses
RESPONSE_TRANSLATIONS = {
    'Fake News': {
        'en': 'Fake News',
        'hi': 'फर्जी खबर',
        'gu': 'ખોટા સમાચાર'
    },
    'Real News': {
        'en': 'Real News',
        'hi': 'सच्ची खबर',
        'gu': 'સાચા સમાચાર'
    },
    'High': {
        'en': 'High',
        'hi': 'उच्च',
        'gu': 'ઉચ્ચ'
    },
    'Medium': {
        'en': 'Medium',
        'hi': 'मध्यम',
        'gu': 'મધ્યમ'
    },
    'Low': {
        'en': 'Low',
        'hi': 'कम',
        'gu': 'નીચું'
    },
    'Confidence': {
        'en': 'Confidence',
        'hi': 'विश्वास',
        'gu': 'વિશ્વાસ'
    },
    'Reliability': {
        'en': 'Reliability',
        'hi': 'विश्वसनीयता',
        'gu': 'વિશ્વસનીયતા'
    }
}

def get_translated_response(key: str, lang_code: str) -> str:
    """
    Get predefined translation for common responses.
    
    Args:
        key: Response key (e.g., 'Fake News', 'Real News')
        lang_code: Target language code
        
    Returns:
        Translated text
    """
    if key in RESPONSE_TRANSLATIONS:
        return RESPONSE_TRANSLATIONS[key].get(lang_code, key)
    return key
