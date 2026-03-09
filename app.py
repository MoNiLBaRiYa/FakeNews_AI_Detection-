from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from functools import wraps
import joblib
from Backend.FND import fetch_and_predict_news, predict_news, predict_news_with_details, find_article_source  # Import from Backend
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from config import config

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

# MongoDB Connection with error handling
try:
    client = MongoClient(app.config.get('MONGODB_URI', 'mongodb://127.0.0.1:27017/'))
    db = client[app.config.get('DATABASE_NAME', 'user_auth_db')]
    users = db['users']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    users = None

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
def login():
    if getattr(app, 'users', users) is None:
         return jsonify({'message': 'Database service unavailable'}), 500
    data = request.json
    email_or_username = data.get('email')
    password = data.get('password')

    # Try to find user by email or username
    user = users.find_one({'$or': [{'email': email_or_username}, {'username': email_or_username}]})
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        session['username'] = user.get('username', email_or_username)
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid email or password'}), 401

#  Route: Forgot Password
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
    return render_template('dashboard.html')

# Route: Fake News Detection Page
@app.route('/fakenews')
@login_required
def fakenews():
    return render_template('truthguard_new.html')

# Route: Analyzer (alias for fakenews)
@app.route('/analyzer')
@login_required
def analyzer():
    return render_template('truthguard_new.html')

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
def threat_map():
    return render_template('threat-map.html')

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

#  Route: Fetch Real-Time News (Dynamic Query-Based with City-Level Location and Language Support)
@app.route('/fetch_news', methods=['GET'])
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
        if city and city not in ["latest", "news", "gujarat", "india", "international"]:
            # Enhance query with city name for hyperlocal news
            enhanced_query = f"{city} {district} {state} news".strip()
            if query not in ["latest", city.lower()]:
                enhanced_query = f"{query} {city} {district} {state}".strip()
            
            print(f"[NEWS] Fetching localized news for: {city}, {district}, {state} in {language}")
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
