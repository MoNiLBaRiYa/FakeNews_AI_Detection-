"""Main Flask application for Fake News Detection."""
from flask import Flask, jsonify, request, render_template, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import joblib
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import config
from Backend.FND import fetch_and_predict_news
from Backend.validators import validate_email, validate_password, validate_text_input, sanitize_input
from Backend.analytics import get_user_statistics, get_global_statistics
from Backend.language_support import (
    detect_language, 
    translate_to_english, 
    get_language_name,
    get_translated_response
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder="../Frontend/templates", 
            static_folder="../Frontend/static")

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
cache = Cache(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[app.config['RATELIMIT_DEFAULT']] if app.config['RATELIMIT_ENABLED'] else []
)

# MongoDB Connection
try:
    client = MongoClient(app.config['MONGODB_URI'], serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    db = client[app.config['DATABASE_NAME']]
    users = db['users']
    predictions_log = db['predictions']
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    users = None
    predictions_log = None

# Load ML model
model = None
try:
    model = joblib.load(app.config['MODEL_PATH'])
    logger.info("ML model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ML model: {e}")

# Utility Functions
def clean_text(text):
    """Preprocess text for prediction."""
    import re
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def log_prediction(email, text, prediction):
    """Log prediction to database."""
    if predictions_log is not None:
        try:
            predictions_log.insert_one({
                'email': email,
                'text': text[:200],  # Store first 200 chars
                'prediction': prediction,
                'timestamp': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")

# Security Headers
@app.after_request
def set_security_headers(response):
    """Set security headers for all responses."""
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Enforce HTTPS (only in production)
    if not app.config['DEBUG']:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

# Routes
@app.route('/')
def home():
    """Render login page."""
    return render_template('loginpage.html')

@app.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    """Handle user registration."""
    if users is None:
        return jsonify({'message': 'Database unavailable'}), 503
    
    try:
        data = request.json
        email = sanitize_input(data.get('email', '')).strip()
        password = data.get('password', '')

        # Validation using validators module
        is_valid_email, email_error = validate_email(email)
        if not is_valid_email:
            return jsonify({'message': email_error}), 400
        
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            return jsonify({'message': password_error}), 400

        # Check if user exists
        if users.find_one({'email': email}):
            return jsonify({'message': 'Email already exists'}), 400

        # Create user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users.insert_one({
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'prediction_count': 0
        })
        
        logger.info(f"New user registered: {email}")
        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Handle user login."""
    if users is None:
        return jsonify({'message': 'Database unavailable'}), 503
    
    try:
        data = request.json
        email = sanitize_input(data.get('email', '')).strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_email'] = email
            session['login_time'] = datetime.utcnow().isoformat()
            
            # Update last login
            users.update_one(
                {'email': email},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            logger.info(f"User logged in: {email}")
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'email': email,
                    'prediction_count': user.get('prediction_count', 0)
                }
            }), 200
        
        logger.warning(f"Failed login attempt for: {email}")
        return jsonify({'message': 'Invalid email or password'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({'message': 'Login failed'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    email = session.get('user_email')
    session.clear()
    if email:
        logger.info(f"User logged out: {email}")
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/forgot_password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Handle password reset request."""
    if users is None:
        return jsonify({'message': 'Database unavailable'}), 503
    
    try:
        data = request.json
        email = sanitize_input(data.get('email', '')).strip()

        is_valid, error = validate_email(email)
        if not is_valid:
            return jsonify({'message': error}), 400

        user = users.find_one({'email': email})
        if user:
            # TODO: Implement actual email sending with token
            logger.info(f"Password reset requested for: {email}")
            return jsonify({'message': 'Password reset link sent to your email'}), 200
        
        # Don't reveal if email exists (security best practice)
        return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
    
    except Exception as e:
        logger.error(f"Password reset error: {e}", exc_info=True)
        return jsonify({'message': 'Password reset failed'}), 500

@app.route('/fakenews')
def fakenews():
    """Render fake news detection page."""
    return render_template('fakenews.html')

@app.route('/predict', methods=['POST'])
@limiter.limit("30 per minute")
def predict():
    """Predict if news is fake or real with multi-language support."""
    if model is None:
        return jsonify({'error': 'Model not available'}), 503
    
    try:
        data = request.json
        original_text = sanitize_input(data.get('text', '')).strip()

        # Validate input using validators module
        is_valid, error = validate_text_input(original_text)
        if not is_valid:
            return jsonify({'error': error}), 400

        # Detect language
        detected_lang = detect_language(original_text)
        lang_name = get_language_name(detected_lang)
        
        logger.info(f"Detected language: {lang_name} ({detected_lang})")
        
        # Translate to English if needed
        text_for_prediction = original_text
        if detected_lang != 'en':
            text_for_prediction, _ = translate_to_english(original_text, detected_lang)
            logger.info(f"Translated text for prediction")

        # Preprocess and predict
        processed_text = clean_text(text_for_prediction)
        if not processed_text:
            return jsonify({'error': 'Text contains no valid content'}), 400
        
        prediction = model.predict([processed_text])
        result = 'Fake News' if prediction[0] == 0 else 'Real News'
        confidence = model.predict_proba([processed_text])[0]
        confidence_score = float(max(confidence))
        
        # Calculate reliability score
        reliability = "High" if confidence_score > 0.8 else "Medium" if confidence_score > 0.6 else "Low"
        
        # Translate response back to user's language
        translated_result = get_translated_response(result, detected_lang)
        translated_reliability = get_translated_response(reliability, detected_lang)
        
        # Log prediction and update user stats
        user_email = session.get('user_email', 'anonymous')
        log_prediction(user_email, original_text, result)
        
        if user_email != 'anonymous' and users is not None:
            users.update_one(
                {'email': user_email},
                {'$inc': {'prediction_count': 1}}
            )
        
        logger.info(f"Prediction: {result} | Confidence: {confidence_score:.2f} | Language: {lang_name} | User: {user_email}")
        
        return jsonify({
            'prediction': translated_result,
            'prediction_en': result,
            'confidence': round(confidence_score * 100, 2),
            'reliability': translated_reliability,
            'reliability_en': reliability,
            'detected_language': detected_lang,
            'language_name': lang_name,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/fetch_news', methods=['GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=300, query_string=True)
def fetch_news():
    """Fetch and analyze real-time news."""
    try:
        query = request.args.get("query", "latest").strip()
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        result = fetch_and_predict_news(query)
        
        if not result.get('news'):
            return jsonify({'error': 'No news found'}), 404
        
        logger.info(f"News fetched for query: {query}")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"News fetch error: {e}")
        return jsonify({'error': 'Failed to fetch news'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'database_connected': users is not None,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

@app.route('/user/stats', methods=['GET'])
@limiter.limit("20 per minute")
def user_stats():
    """Get user statistics."""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        stats = get_user_statistics(predictions_log, user_email)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/global/stats', methods=['GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=60)
def global_stats():
    """Get global platform statistics."""
    try:
        stats = get_global_statistics(predictions_log)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error fetching global stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500
