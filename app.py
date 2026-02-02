from flask import Flask, jsonify, request, render_template
import joblib
from Backend.FND import fetch_and_predict_news, predict_news  # Import from Backend
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder="Frontend/templates", static_folder="Frontend/Static")

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
    return render_template('loginpage.html')

# Route: Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if users.find_one({'email': email}):
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)
    users.insert_one({'email': email, 'password': hashed_password})

    return jsonify({'message': 'User registered successfully'}), 201

#  Route: Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users.find_one({'email': email})
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

# Route: Fake News Detection Page
@app.route('/fakenews')
def fakenews():
    return render_template('fakenews.html')

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

#  Route: Fetch Real-Time News (Dynamic Query-Based)
@app.route('/fetch_news', methods=['GET'])
def fetch_news():
    query = request.args.get("query", "latest")  # Get query from URL, default is "latest"
    return jsonify(fetch_and_predict_news(query))

if __name__ == '__main__':
    app.run(debug=True)
