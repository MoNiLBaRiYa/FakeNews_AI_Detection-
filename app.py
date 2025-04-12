from flask import Flask, jsonify, request, render_template
import joblib
from FND import fetch_and_predict_news  # Import real-time news fetching function
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder="../Frontend/templates", static_folder="../Frontend/static")

# MongoDB Connection with error handling
try:
    client = MongoClient('mongodb://127.0.0.1:27017/')
    db = client['user_auth_db']
    users = db['users']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    users = None

# Load trained model with error handling
try:
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Model", "model.pkl")
    model = joblib.load(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

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
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
        
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Preprocess text before prediction
        def clean_text(text):
            import re
            text = text.lower()
            text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
            text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
            text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters
            return text

        processed_text = clean_text(text)
        prediction = model.predict([processed_text])
        result = 'Fake News' if prediction[0] == 0 else 'Real News'
        
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

#  Route: Fetch Real-Time News (Dynamic Query-Based)
@app.route('/fetch_news', methods=['GET'])
def fetch_news():
    query = request.args.get("query", "latest")  # Get query from URL, default is "latest"
    return jsonify(fetch_and_predict_news(query))

if __name__ == '__main__':
    app.run(debug=True)
