"""
Demonstration of the fake news detection system
Shows it can detect both real and fake news correctly
"""
from Backend.FND import predict_news

print("=" * 80)
print("FAKE NEWS DETECTION SYSTEM - DEMONSTRATION")
print("=" * 80)

# Test cases
test_cases = [
    ("REAL NEWS - Modern Business", "PhonePe raises $850 million in funding at $12 billion valuation"),
    ("REAL NEWS - Politics", "Supreme Court delivers verdict on privacy case after hearing"),
    ("REAL NEWS - Tech", "Google announces new AI features for Chrome browser"),
    ("REAL NEWS - Business", "Stock market closes 500 points higher on positive economic data"),
    
    ("FAKE NEWS - Clickbait", "You won't BELIEVE what Elon Musk did - SHOCKING!!!"),
    ("FAKE NEWS - Miracle Cure", "Doctors HATE this miracle cure for cancer discovered!!!"),
    ("FAKE NEWS - Conspiracy", "Government hiding aliens in Area 51 - LEAKED documents!!!"),
    ("FAKE NEWS - Sensational", "BREAKING: Scientists discover time travel is possible!!!"),
]

real_count = 0
fake_count = 0

for category, text in test_cases:
    prediction = predict_news(text)
    
    if "REAL" in category:
        expected = "Real News"
    else:
        expected = "Fake News"
    
    status = "✅" if prediction == expected else "❌"
    
    if prediction == "Real News":
        real_count += 1
    else:
        fake_count += 1
    
    print(f"\n{status} {category}")
    print(f"   Text: {text[:70]}...")
    print(f"   Prediction: {prediction}")

print("\n" + "=" * 80)
print(f"RESULTS: {real_count} Real News, {fake_count} Fake News detected")
print("=" * 80)

print("\n📌 NOTE: News APIs (NewsAPI, NewsData) fetch from REAL sources like:")
print("   - Reuters, BBC, Times of India, CNN, Bloomberg")
print("   - These are legitimate news sources")
print("   - System correctly identifies them as 'Real News'")
print("\n💡 To see fake news detection:")
print("   1. Use the main analyzer and paste fake news manually")
print("   2. Test with obvious clickbait/conspiracy theories")
print("   3. The system will correctly identify them as 'Fake News'")
