"""
Train a specialized model for news headlines (short text)
Optimized for 10-100 word headlines vs full articles
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import re
import os

def clean_headline(text):
    """Clean headline text for training"""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Keep letters, numbers, and basic punctuation
    text = re.sub(r'[^a-z0-9\s\.\,\!\?]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def train_headline_model():
    """Train headline-specific fake news detection model"""
    print("=" * 70)
    print("🎯 HEADLINE MODEL TRAINING")
    print("=" * 70)
    
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'Headlines_Large.csv')
    
    if not os.path.exists(dataset_path):
        # Fallback to small dataset
        dataset_path = os.path.join(os.path.dirname(__file__), 'Headlines.csv')
        if not os.path.exists(dataset_path):
            print("❌ No headline dataset found!")
            print("   Run create_large_headline_dataset.py first")
            return
    
    print(f"\n📂 Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    print(f"✅ Loaded {len(df)} headlines")
    print(f"   Real: {len(df[df['label'] == 1])}")
    print(f"   Fake: {len(df[df['label'] == 0])}")
    
    # Clean text
    print("\n🧹 Cleaning headlines...")
    df['text_clean'] = df['text'].apply(clean_headline)
    
    # Remove empty entries
    df = df[df['text_clean'].str.len() > 10]
    print(f"✅ {len(df)} headlines after cleaning")
    
    # Split data
    X = df['text_clean']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📊 Dataset Split:")
    print(f"   Training: {len(X_train)} headlines")
    print(f"   Testing: {len(X_test)} headlines")
    
    # Train multiple models and compare
    models = {
        'Naive Bayes': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=3000,
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=2,
                max_df=0.8
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ]),
        'Logistic Regression': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=3000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )),
            ('classifier', LogisticRegression(max_iter=1000, C=1.0))
        ]),
        'Random Forest': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=2000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
    }
    
    print("\n🤖 Training models...")
    print("-" * 70)
    
    best_model = None
    best_accuracy = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"\n📈 Training {name}...")
        
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ {name} Accuracy: {accuracy * 100:.2f}%")
        
        # Detailed metrics
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['Fake', 'Real'],
                                   digits=4))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\nConfusion Matrix:")
        print(f"              Predicted")
        print(f"              Fake  Real")
        print(f"Actual Fake   {cm[0][0]:4d}  {cm[0][1]:4d}")
        print(f"       Real   {cm[1][0]:4d}  {cm[1][1]:4d}")
        
        # Track best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
        
        print("-" * 70)
    
    # Save best model
    print(f"\n🏆 Best Model: {best_name} ({best_accuracy * 100:.2f}%)")
    
    model_path = os.path.join(os.path.dirname(__file__), 'model_headlines.pkl')
    joblib.dump(best_model, model_path)
    
    print(f"✅ Model saved to: {model_path}")
    
    # Test with sample headlines
    print("\n🧪 Testing with sample headlines:")
    print("-" * 70)
    
    test_samples = [
        ("Budget 2026 Live Streaming: FM Nirmala Sitharaman budget speech", "Real"),
        ("SHOCKING: Elon Musk admits aliens control the world!!!", "Fake"),
        ("Supreme Court delivers verdict on privacy case", "Real"),
        ("You won't BELIEVE what Bill Gates did - EXPOSED!", "Fake"),
        ("India's GDP growth rate reaches 7.2% in Q3", "Real"),
        ("Doctors HATE this miracle cure for cancer!!!", "Fake"),
    ]
    
    for headline, expected in test_samples:
        cleaned = clean_headline(headline)
        prediction = best_model.predict([cleaned])[0]
        result = "Real" if prediction == 1 else "Fake"
        status = "✅" if result == expected else "❌"
        
        print(f"\n{status} Headline: {headline}")
        print(f"   Expected: {expected} | Predicted: {result}")
    
    print("\n" + "=" * 70)
    print("🎉 HEADLINE MODEL TRAINING COMPLETE!")
    print("=" * 70)
    
    return model_path

if __name__ == "__main__":
    train_headline_model()
