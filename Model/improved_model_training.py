"""
Improved Fake News Detection Model with Enhanced Features
This version includes multiple improvements for better accuracy
"""

import pandas as pd
import numpy as np
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Common English stopwords (no NLTK needed)
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

class ImprovedTextPreprocessor:
    """Enhanced text preprocessing with more sophisticated cleaning"""
    
    def __init__(self):
        self.stop_words = STOPWORDS
    
    def clean_text(self, text):
        """Advanced text cleaning"""
        if not isinstance(text, str):
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
        
        # Remove stopwords
        words = text.split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        text = ' '.join(words)
        
        return text



def train_improved_model():
    """Train an improved model with better accuracy"""
    
    print("Loading datasets...")
    true_df = pd.read_csv("True.csv")
    fake_df = pd.read_csv("Fake.csv")
    
    # Assign labels
    true_df['label'] = 1
    fake_df['label'] = 0
    
    # Merge and shuffle
    df = pd.concat([true_df, fake_df], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Keep only text and label
    df = df[['text', 'label']]
    
    print("Preprocessing text...")
    preprocessor = ImprovedTextPreprocessor()
    df['text'] = df['text'].apply(preprocessor.clean_text)
    
    # Remove empty texts
    df = df[df['text'].str.len() > 10]
    
    print(f"Dataset size: {len(df)} articles")
    
    # Split data
    X = df['text']
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\n=== Training Model 1: Logistic Regression ===")
    lr_model = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),  # Use unigrams and bigrams
            min_df=2,
            max_df=0.95
        )),
        ('lr', LogisticRegression(max_iter=1000, C=1.0, random_state=42))
    ])
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    lr_accuracy = accuracy_score(y_test, lr_pred)
    print(f"Logistic Regression Accuracy: {lr_accuracy:.4f}")
    
    print("\n=== Training Model 2: Random Forest ===")
    rf_model = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2
        )),
        ('rf', RandomForestClassifier(
            n_estimators=100,
            max_depth=50,
            random_state=42,
            n_jobs=-1
        ))
    ])
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
    
    print("\n=== Training Model 3: Naive Bayes (Original) ===")
    nb_model = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('nb', MultinomialNB())
    ])
    nb_model.fit(X_train, y_train)
    nb_pred = nb_model.predict(X_test)
    nb_accuracy = accuracy_score(y_test, nb_pred)
    print(f"Naive Bayes Accuracy: {nb_accuracy:.4f}")
    
    # Choose best model
    models = [
        ('lr', lr_model, lr_accuracy),
        ('rf', rf_model, rf_accuracy),
        ('nb', nb_model, nb_accuracy)
    ]
    best_name, best_model, best_accuracy = max(models, key=lambda x: x[2])
    
    print(f"\n=== Best Model: {best_name.upper()} with {best_accuracy:.4f} accuracy ===")
    
    # Detailed evaluation
    y_pred = best_model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Fake', 'Real']))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save the best model
    print("\nSaving model...")
    joblib.dump(best_model, "model_improved.pkl")
    print("✅ Improved model saved as model_improved.pkl")
    
    return best_model, best_accuracy

if __name__ == "__main__":
    model, accuracy = train_improved_model()
    print(f"\n🎯 Final Model Accuracy: {accuracy:.2%}")
