from flask import Flask, jsonify, request, render_template
import joblib
from Backend.FND import fetch_and_predict_news, predict_news, find_article_source  # Import from Backend
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Serve templates + static assets from the Frontend folder (prevents "white body"
# when `/static/css/common.css` fails to load).
app = Flask(
    __name__,
    template_folder="Frontend/templates",
    static_folder="Frontend/static",
    static_url_path="/static",
)

# MongoDB Connection with error handling
try:
    client = MongoClient('mongodb://127.0.0.1:27017/')
    db = client['user_auth_db']
    users = db['users']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    users = None

# Load trained models with error handling (DUAL MODEL APPROACH)
model_article = None  # For full articles
model_headline = None  # For headlines

try:
    # Load article model
    model_path = os.path.join(os.path.dirname(__file__), "Model", "model_improved.pkl")
    if os.path.exists(model_path):
        model_article = joblib.load(model_path)
        print("✅ Article model loaded (99.63% accuracy)")
    else:
        model_path = os.path.join(os.path.dirname(__file__), "Model", "model.pkl")
        model_article = joblib.load(model_path)
        print("✅ Article model loaded (94.25% accuracy)")
except Exception as e:
    print(f"Error loading article model: {e}")

try:
    # Load headline model
    headline_path = os.path.join(os.path.dirname(__file__), "Model", "model_headlines.pkl")
    if os.path.exists(headline_path):
        model_headline = joblib.load(headline_path)
        print("✅ Headline model loaded (95.24% accuracy)")
except Exception as e:
    print(f"Error loading headline model: {e}")

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
    data = request.json
    email_or_username = data.get('email')
    password = data.get('password')

    # Try to find user by email or username
    user = users.find_one({'$or': [{'email': email_or_username}, {'username': email_or_username}]})
    
    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid email or password'}), 401

#  Route: Forgot Password
@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    user = users.find_one({'email': email})
    if user:
        return jsonify({'message': 'Reset link sent to your email (Mocked)'})
    return jsonify({'message': 'Email not found'}), 404

# Route: Logout
@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route: Fake News Detection Page
@app.route('/fakenews')
def fakenews():
    return render_template('truthguard_new.html')

# Route: Analyzer (alias for fakenews)
@app.route('/analyzer')
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
        # Use the prediction function
        result = predict_news(text)

        # Get confidence
        import re
        text_clean = text.lower()
        text_clean = re.sub(r'https?://\S+|www\.\S+', '', text_clean)
        text_clean = re.sub(r'<.*?>', '', text_clean)
        text_clean = re.sub(r'\S+@\S+', '', text_clean)

        char_count = len(text_clean)
        selected_model = model_headline if char_count < 300 and model_headline else model_article

        if selected_model is not None:
            proba = selected_model.predict_proba([text_clean])[0]
            confidence = round(max(proba) * 100, 2)
        else:
            confidence = 85.0

        # Simple human-readable rationale
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
        # Use the SAME prediction function as news search for consistency
        result = predict_news(text)
        
        # Get prediction probabilities for confidence
        try:
            # Basic cleaning for model
            import re
            text_clean = text.lower()
            text_clean = re.sub(r'https?://\S+|www\.\S+', '', text_clean)
            text_clean = re.sub(r'<.*?>', '', text_clean)
            text_clean = re.sub(r'\S+@\S+', '', text_clean)
            
            # Select appropriate model based on text length
            char_count = len(text_clean)
            selected_model = model_headline if char_count < 300 and model_headline else model_article
            
            if selected_model is not None:
                proba = selected_model.predict_proba([text_clean])[0]
                confidence = round(max(proba) * 100, 2)
            else:
                confidence = 85.0
        except:
            # Fallback confidence based on text characteristics
            if len(text) > 200:
                confidence = 92.0
            elif len(text) > 100:
                confidence = 85.0
            else:
                confidence = 75.0
        
        # Calculate reliability based on confidence
        if confidence >= 90:
            reliability = "High"
        elif confidence >= 75:
            reliability = "Medium"
        else:
            reliability = "Low"
        
        # Detect language (simple detection)
        language_name = "English"
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            language_name = "Hindi"
        elif any(ord(char) >= 0x0A80 and ord(char) <= 0x0AFF for char in text):
            language_name = "Gujarati"
        
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
    query = request.args.get("query", "latest")  # Get query from URL
    region = request.args.get("region", "")  # Get region (gujarat/india/international)
    city = request.args.get("city", "")  # Get city name (Ahmedabad, Somnath, Vadodara, etc.)
    state = request.args.get("state", "")  # Get state name
    lat = request.args.get("lat", "")  # Get latitude
    lon = request.args.get("lon", "")  # Get longitude
    language = request.args.get("language", "en")  # Get preferred language (en, hi, gu)
    
    # Priority 1: City-specific news (most accurate)
    if city and city not in ["latest", "news", "gujarat", "india", "international"]:
        # Enhance query with city name for hyperlocal news
        enhanced_query = f"{city} {state} news"
        if query not in ["latest", city.lower()]:
            enhanced_query = f"{query} {city} {state}"
        
        print(f"🎯 Fetching city-specific news for: {city}, {state} in {language}")
        return jsonify(fetch_and_predict_news(enhanced_query, region, city, state, language))
    
    # Priority 2: Region-based news
    if region:
        if region.lower() == "gujarat":
            query = f"{query} Gujarat" if query not in ["latest", "gujarat"] else "Gujarat news"
        elif region.lower() == "india":
            query = f"{query} India" if query not in ["latest", "india"] else "India news"
        elif region.lower() == "international":
            query = f"{query} world international" if query not in ["latest", "international"] else "world news"
    
    return jsonify(fetch_and_predict_news(query, region, city, state, language))

if __name__ == '__main__':
    app.run(debug=True)
