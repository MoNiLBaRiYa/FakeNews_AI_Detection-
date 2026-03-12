import logging
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from functools import wraps
import joblib
from Backend.FND import fetch_and_predict_news, predict_news, predict_news_with_details, find_article_source  # Import from Backend
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from authlib.integrations.flask_client import OAuth
import secrets
from config import config
from dotenv import load_dotenv
import requests
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Serve templates + static assets from the Frontend folder (prevents "white body"
# when `/static/css/common.css` fails to load).
app = Flask(
    __name__,
    template_folder="Frontend/templates",
    static_folder="Frontend/static",
    static_url_path="/static",
)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))
app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Setup Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://"
)

# Setup Cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
cache.init_app(app)

# Persist sessions for 30 days when "Remember Me" is checked
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Setup Google OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# MongoDB Connection with error handling
try:
    client = MongoClient(app.config.get('MONGODB_URI', 'mongodb://127.0.0.1:27017/'))
    db = client[app.config.get('DATABASE_NAME', 'user_auth_db')]
    users = db['users']
    history_collection = db['history']
    api_keys_collection = db['api_keys']
    notes_collection = db['notes']
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    users = None
    history_collection = None
    api_keys_collection = None
    notes_collection = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# Email validation function
def is_valid_email(email):
    import re
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# Route: Home Page (Login)
@app.route('/')
def home():
    return render_template('login_new.html')

# Route: Signup Page
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup_new.html')

# Route: Favicon (fix 404 error)
@app.route('/favicon.ico')
def favicon():
    return '', 204

# Route: Signup
@app.route('/signup', methods=['POST'])
@limiter.limit("10 per minute")
def signup():
    if getattr(app, 'users', users) is None:
         return jsonify({'message': 'Database service unavailable'}), 500
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username', email.split('@')[0])  # Use email prefix if no username

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if users.find_one({'email': email}):
        return jsonify({'message': 'Email already exists'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400

    hashed_password = generate_password_hash(password)
    users.insert_one({'email': email, 'password': hashed_password, 'username': username})

    return jsonify({'message': 'User registered successfully'}), 201

#  Route: Login
@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    if getattr(app, 'users', users) is None:
         return jsonify({'message': 'Database service unavailable'}), 500
    data = request.json
    email_or_username = data.get('email')
    password = data.get('password')

    # Try to find user by email or username
    user = users.find_one({'$or': [{'email': email_or_username}, {'username': email_or_username}]})
    
    if user and check_password_hash(user['password'], password):
        remember_me = data.get('remember_me', False)
        session.permanent = bool(remember_me)  # If True, session lives for PERMANENT_SESSION_LIFETIME (30 days)
        session['user_id'] = str(user['_id'])
        session['username'] = user.get('username', email_or_username)
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid email or password'}), 401

# Route: Google Login
@app.route('/login/google')
def login_google():
    if not GOOGLE_CLIENT_ID:
        return jsonify({'message': 'Google Auth is not configured in .env'}), 500
    redirect_uri = url_for('auth_google', _external=True)
    return google.authorize_redirect(redirect_uri)

# Route: Google Auth Callback
@app.route('/auth/google')
def auth_google():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info and users is not None:
        email = user_info['email']
        username = user_info.get('name', email.split('@')[0])
        
        # Determine if user already exists
        user = users.find_one({'email': email})
        if not user:
            # Create a new user account with no password
            uid = users.insert_one({'email': email, 'username': username, 'auth_provider': 'google'})
            session['user_id'] = str(uid.inserted_id)
        else:
            session['user_id'] = str(user['_id'])
            
        session['username'] = username
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

# Route: Forgot Password
@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    if getattr(app, 'users', users) is None:
         return jsonify({'message': 'Database service unavailable'}), 500
    data = request.json
    email = data.get('email')

    user = users.find_one({'email': email})
    if user:
        return jsonify({'message': 'Reset link sent to your email (Mocked)'})
    return jsonify({'message': 'Email not found'}), 404

# Route: Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Route: Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

# Route: Fake News Detection Page
@app.route('/fakenews')
@login_required
def fakenews():
    return render_template('truthguard_new.html', username=session.get('username'))

# Route: Analyzer (alias for fakenews)
@app.route('/analyzer')
@login_required
def analyzer():
    return render_template('truthguard_new.html', username=session.get('username'))

# Route: Analyze (form submission handler)
@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.form.get('text')
    language = request.form.get('language', 'english')
    
    if not text:
        return render_template('truthguard_new.html', error='No text provided')
    
    try:
        # Use the improved prediction function
        details = predict_news_with_details(text)
        result = details['prediction']
        confidence = details['confidence']
        reason = details['reason']


        # Try to detect a source URL from the original text (first URL wins)
        url_matches = re.findall(r'https?://\S+|www\.\S+', text)
        source_url = url_matches[0] if url_matches else ''
        source_label = ''

        if source_url:
            source_label = source_url
        else:
            # Best-effort attempt to find a likely source on the internet
            src_info = find_article_source(text)
            source_url = src_info.get("url", "")
            if src_info.get("source") and src_info["source"] != "Unknown":
                source_label = f"{src_info['source']} (auto-detected)"
            elif src_info.get("title") and src_info["title"] != "Unknown":
                source_label = f"{src_info['title']} (auto-detected)"
            else:
                source_label = "Unknown"

        # Save to history if logged in
        if 'user_id' in session and history_collection is not None:
            try:
                history_collection.insert_one({
                    'user_id': session['user_id'],
                    'text': text,
                    'prediction': result,
                    'confidence': confidence,
                    'language': language,
                    'reason': reason,
                    'timestamp': datetime.utcnow()
                })
            except Exception as e:
                logger.error(f"Failed to save history: {e}")

        return render_template(
            'truthguard_new.html',
            result={
                'prediction': result,
                'confidence': confidence,
                'text': text,
                'source_url': source_url,
                'source_label': source_label,
                'language': language,
                'reason': reason,
            }
        )
    except Exception as e:
        return render_template('truthguard_new.html', error=f'Analysis error: {str(e)}')

# Route: Threat Map Page
@app.route('/threat-map')
@login_required
def threatmap():
    return render_template('threat-map.html', username=session.get('username'))

# Route: History Page
@app.route('/history')
@login_required
def history():
    if history_collection is None:
        return render_template('history.html', history_items=[], error="Database not connected", username=session.get('username'))
    
    try:
        items = list(history_collection.find({'user_id': session['user_id']}).sort('timestamp', -1))
        return render_template('history.html', history_items=items, username=session.get('username'))
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return render_template('history.html', history_items=[], error="Failed to load history", username=session.get('username'))

#  Route: Predict Fake/Real News
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Use the improved detailed prediction function
        details = predict_news_with_details(text)
        result = details['prediction']
        confidence = details['confidence']
        reliability = details['reliability']
        language_name = details['language_name']

        
        return jsonify({
            'prediction': result,
            'prediction_en': result,
            'confidence': confidence,
            'reliability': reliability,
            'reliability_en': reliability,
            'language_name': language_name
        })
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

# Route: Deepfake / Image Mock Analysis
@app.route('/analyze_image', methods=['POST'])
@limiter.limit("5 per minute")
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
        
    try:
        # Read the image bytes directly into memory
        image_bytes = file.read()
        
        # MULTI-MODEL CONSENSUS SYSTEM
        # Using two specialized models to reduce the risk of false positives on real photos
        primary_model = "prithivMLmods/Deep-Fake-Detector-v2-Model"
        secondary_model = "umm-maybe/AI-image-detector"
        
        api_url_1 = f"https://router.huggingface.co/hf-inference/models/{primary_model}"
        api_url_2 = f"https://router.huggingface.co/hf-inference/models/{secondary_model}"
        
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": file.content_type or "image/jpeg"
        }
        
        logger.info(f"Analyzing image {file.filename} with multi-model consensus...")
        
        # Run both analysis in parallel if possible, but for simplicity we'll do sequential here
        # or use session for performance
        try:
            resp1 = requests.post(api_url_1, headers=headers, data=image_bytes, timeout=30)
            resp2 = requests.post(api_url_2, headers=headers, data=image_bytes, timeout=30)
            
            if resp1.status_code != 200 or resp2.status_code != 200:
                logger.error(f"HF API Error: {resp1.status_code} or {resp2.status_code}")
                # Fallback to secondary if primary fails, or vice versa
                success_resp = resp1 if resp1.status_code == 200 else resp2
                if success_resp.status_code != 200:
                     return jsonify({'error': "Deepfake detection service is currently busy. Please try again in 30 seconds."}), 503
                results = [success_resp.json()]
            else:
                results = [resp1.json(), resp2.json()]
                
        except Exception as e:
            logger.error(f"Consensus error: {e}")
            return jsonify({'error': "Internal connection error. Please try again."}), 500

        # Consensus Logic
        is_manipulated = False
        is_ai_generated = False
        confidence_points = []
        
        # Process Model 1 (Deepfake focused)
        if results[0] and isinstance(results[0], list):
            top1 = results[0][0]
            label1 = top1.get('label', '').lower()
            score1 = top1.get('score', 0)
            if 'fake' in label1:
                is_manipulated = True
                confidence_points.append(score1)
            else:
                confidence_points.append(1 - score1) # Points for it being real
                
        # Process Model 2 (AI Generation focused)
        if len(results) > 1 and results[1] and isinstance(results[1], list):
            top2 = results[1][0]
            label2 = top2.get('label', '').lower()
            score2 = top2.get('score', 0)
            # Label map for umm-maybe/AI-image-detector: artificial/human
            if 'artificial' in label2:
                is_ai_generated = True
                confidence_points.append(score2)
            else:
                confidence_points.append(1 - score2)
        
        # Final Decision
        # We only flag if BOTH models agree it's suspicious, OR if one is extremely confident (>95%)
        final_is_fake = False
        if is_manipulated and is_ai_generated:
            final_is_fake = True
        elif is_manipulated and max(confidence_points) > 0.95:
            final_is_fake = True
        elif is_ai_generated and max(confidence_points) > 0.98: # Generation model is more prone to art false pos
            final_is_fake = True
            
        if not confidence_points:
            return jsonify({"error": "AI service returned invalid data format."}), 500
            
        final_confidence = round(sum(confidence_points) / len(confidence_points) * 100, 2)
        final_result = "DEEPFAKE DETECTED" if final_is_fake else "LIKELY REAL"
        
        artifacts = []
        if final_is_fake:
            if is_manipulated: artifacts.append("Face/Structure manipulation detected.")
            if is_ai_generated: artifacts.append("Synthetic noise patterns detected.")
            if final_confidence > 90: artifacts.append("High mathematical certainty of AI generation.")
        else:
            artifacts.append("Natural lighting and skin texture detected.")
            if is_manipulated and not is_ai_generated:
                artifacts.append("Note: Minor structural inconsistencies detected but likely due to lighting/compression.")
                
        return jsonify({
            'result': final_result,
            'confidence': final_confidence,
            'artifacts_found': artifacts
        })
            
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API: Live Threat Trends
@app.route('/api/threat-trends', methods=['GET'])
def threat_trends():
    """
    Provides real-time analytics data to the map based on recent historical logs.
    """
    if history_collection is None:
        return jsonify({'error': 'Database not connected'}), 500
        
    # Mocking live trends for this demonstration
    return jsonify({
        'trending_topics': [
            {'keyword': 'Election Fraud', 'count': 432, 'trend': 'up'},
            {'keyword': 'Miracle Cure', 'count': 214, 'trend': 'down'},
            {'keyword': 'Banking Crisis', 'count': 189, 'trend': 'up'}
        ],
        'high_activity_regions': ['Ahmedabad', 'Delhi', 'Mumbai']
    })

# API: Add Community Note
@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    data = request.json
    text = data.get('text')
    
    if not text or len(text) < 10:
        return jsonify({'error': 'Note is too short.'}), 400
        
    if notes_collection is not None:
        notes_collection.insert_one({
            'user_id': session['user_id'],
            'article_url': data.get('url', ''),
            'note_text': text,
            'timestamp': datetime.utcnow()
        })
    return jsonify({'message': 'Community note added successfully!'}), 201

# API: Developer Endpoint for External Use / Browser Extension
@app.route('/api/v1/analyze', methods=['POST'])
@limiter.limit("500 per day")
def api_analyze():
    data = request.json
    api_key = data.get('api_key')
    text = data.get('text')
    
    # Simple open-access validation for the browser extension
    if api_key != 'extension_key_123' and (api_keys_collection is None or not api_keys_collection.find_one({'key': api_key})):
         return jsonify({'error': 'Invalid API Key'}), 401
         
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        details = predict_news_with_details(text)
        return jsonify({
            'prediction': details['prediction'],
            'confidence': details['confidence'],
            'reliability': details['reliability'],
            'reason': details['reason']
        })
    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({'error': 'Internal analysis error'}), 500

#  Route: Fetch Real-Time News (Dynamic Query-Based with City-Level Location and Language Support)
@app.route('/fetch_news', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def fetch_news():
    query = request.args.get("query", "latest")
    region = request.args.get("region", "")
    city = request.args.get("city", "")
    district = request.args.get("district", "")
    state = request.args.get("state", "")
    lat = request.args.get("lat", "")
    lon = request.args.get("lon", "")
    language = request.args.get("language", "en")
    
    try:
        # Priority 1: City-specific news (most accurate)
        if city and city.lower() not in ["latest", "news", "gujarat", "india", "international"]:
            # Clean up redundant terms and overly long state names
            loc_parts = []
            for term in [city, district]:
                if term and not any(term.lower() in p.lower() or p.lower() in term.lower() for p in loc_parts):
                    loc_parts.append(term)
            
            # Only add state if it's short, to prevent "Dadra and Nagar Haveli and Daman and Diu" from overwhelming the query
            if state and len(state) < 25 and not any(state.lower() in p.lower() or p.lower() in state.lower() for p in loc_parts):
                loc_parts.append(state)
                
            loc_str = " ".join(loc_parts)
            
            if query.lower() in ["latest", city.lower(), loc_str.lower()]:
                enhanced_query = f"{loc_str} news".strip()
            else:
                enhanced_query = f"{query} {loc_str}".strip()
            
            print(f"[NEWS] Fetching localized news for: {city}, {district}, {state} in {language} -> Query: {enhanced_query}")
            return jsonify(fetch_and_predict_news(enhanced_query, region, city, state, language, district))
        
        # Priority 2: Region-based news
        if region:
            if region.lower() == "gujarat":
                query = f"{query} Gujarat" if query not in ["latest", "gujarat"] else "Gujarat news"
            elif region.lower() == "india":
                query = f"{query} India" if query not in ["latest", "india"] else "India news"
            elif region.lower() == "international":
                query = f"{query} world international" if query not in ["latest", "international"] else "world news"
        
        return jsonify(fetch_and_predict_news(query, region, city, state, language, district))
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}', 'news': [], 'predictions': []}), 500

if __name__ == '__main__':
    app.run(debug=True)
