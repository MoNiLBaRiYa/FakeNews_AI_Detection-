# 🛡️ TruthGuard - Fake News Detection System

> **Fighting Misinformation with AI** - A smart tool that helps you identify fake news and verify information authenticity in multiple languages.

---

## 📖 What is TruthGuard?

TruthGuard is an intelligent web application that helps you determine whether a news article or headline is **real** or **fake**. In today's digital age, misinformation spreads rapidly across social media and news platforms. TruthGuard acts as your personal fact-checker, using advanced artificial intelligence to analyze news content and provide instant verification.

### 🎯 Why Do We Need This?

- **Misinformation is Everywhere**: Fake news can influence opinions, elections, and even public health decisions
- **Hard to Verify Manually**: With thousands of news articles published daily, it's impossible to fact-check everything
- **Language Barriers**: Fake news spreads in multiple languages, making it harder to detect
- **Speed Matters**: By the time traditional fact-checkers verify a story, it may have already gone viral

TruthGuard solves these problems by providing **instant, AI-powered verification** in multiple languages including English, Hindi, and Gujarati.

---

## ✨ Key Features

### 🔍 **Instant News Verification**
- Paste any news article, headline, or social media post
- Get immediate results: Real or Fake
- See confidence scores (how sure the AI is about its prediction)
- Understand WHY the content was flagged

### 🌐 **Multi-Language Support**
- **English**: Full support with 99.63% accuracy
- **Hindi (हिंदी)**: Detect fake news in Devanagari script
- **Gujarati (ગુજરાતી)**: Regional language support for Gujarat
- Automatic language detection

### 📰 **Live News Feed**
- Real-time news from trusted Indian sources
- Regional news filtering (Gujarat, India, International)
- City-specific news (Ahmedabad, Mumbai, Delhi, and more)
- Each article is automatically analyzed for authenticity

### 🗺️ **Threat Map**
- Visual representation of fake news spread
- See where misinformation is most active
- Track trends and patterns

### 🔐 **Secure User Accounts**
- Create your personal account
- Save your verification history
- Track your fact-checking activity

---

## 🎓 How Does It Work? (Simple Explanation)

Think of TruthGuard as a **super-smart detective** that has read millions of news articles and learned to spot patterns:

### Step 1: You Provide Content
You paste a news headline or article into the system.

### Step 2: AI Analysis
The system analyzes multiple factors:
- **Language Style**: Does it use sensational words like "SHOCKING!" or "You won't believe..."?
- **Source Credibility**: Does it mention reputable news sources like Reuters, BBC, or Times of India?
- **Professional Indicators**: Does it include proper citations, dates, and specific details?
- **Emotional Manipulation**: Does it try to make you angry or scared without facts?

### Step 3: Prediction
Based on these factors, the AI makes a prediction:
- **Real News**: Content appears authentic and trustworthy
- **Fake News**: Content shows signs of misinformation

### Step 4: Confidence Score
The system tells you how confident it is (e.g., 95% confident this is fake news)

### Step 5: Explanation
You get a human-readable explanation of why the content was classified as real or fake.

---

## 🧠 The Technology Behind It

### Machine Learning Models
- **Dual Model Approach**: 
  - One model specialized for short headlines (95.24% accuracy)
  - Another for full articles (99.63% accuracy)
- **Training Data**: Trained on thousands of verified real and fake news articles
- **Continuous Learning**: Models improve over time with more data

### Smart Detection Methods
1. **Rule-Based Checks**: Identifies obvious fake news patterns (excessive punctuation, ALL CAPS, clickbait phrases)
2. **Source Verification**: Recognizes reputable news organizations
3. **Professional Language Detection**: Looks for journalistic standards
4. **Confidence Thresholds**: Only makes predictions when sufficiently confident

### Web Scraping
- Fetches real-time news from 15+ trusted Indian news sources
- Supports regional and city-specific news
- Respects website policies and rate limits

---

## 🚀 Getting Started

### For Non-Technical Users

**Option 1: Use the Live Website** (Easiest)
1. Visit the TruthGuard website (ask your administrator for the URL)
2. Create an account with your email
3. Start verifying news immediately!

**Option 2: Request Access**
Contact your IT department or project administrator to set up TruthGuard for your organization.

### For Technical Users

#### Prerequisites
- Python 3.8 or higher
- MongoDB (for user authentication)
- Internet connection (for live news fetching)

#### Quick Installation

**Windows Users:**
```batch
# 1. Clone or download the project
cd "CODE/Minor Project New"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env file with your settings

# 5. Run the application
python app.py
```

**Linux/Mac Users:**
```bash
# 1. Navigate to project
cd "CODE/Minor Project New"

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env file with your settings

# 5. Run the application
python app.py
```

#### Using Docker (Recommended for Production)
```bash
# Build and run with Docker Compose
docker-compose up -d
```

The application will be available at: `http://localhost:5000`

---

## 📱 How to Use TruthGuard

### 1. Create an Account
- Go to the signup page
- Enter your email and create a password (minimum 6 characters)
- Click "Sign Up"

### 2. Verify News Content
- Click on "Analyzer" or "Fake News Detection"
- Paste the news article, headline, or social media post
- Select the language (English, Hindi, or Gujarati)
- Click "Analyze"

### 3. Understand the Results
- **Prediction**: Real News or Fake News
- **Confidence**: How sure the AI is (0-100%)
- **Reliability**: High, Medium, or Low
- **Explanation**: Why the content was classified this way
- **Source**: Where the content might have originated

### 4. Browse Live News
- Go to "Dashboard"
- Select region: Gujarat, India, or International
- Select city (optional): Ahmedabad, Mumbai, Delhi, etc.
- Choose language preference
- Browse verified news articles

### 5. View Threat Map
- Click on "Threat Map"
- See visual representation of fake news distribution
- Identify high-risk areas and trending misinformation

---

## 🎯 Accuracy & Reliability

### Model Performance
- **Article Model**: 99.63% accuracy on test data
- **Headline Model**: 95.24% accuracy on test data
- **Multi-language**: Rule-based detection for Hindi and Gujarati

### What This Means
- Out of 100 fake news articles, the system correctly identifies 99-100
- Out of 100 real news articles, the system correctly identifies 95-99
- Very low false positive rate (rarely marks real news as fake)

### Limitations
- **New Patterns**: Very sophisticated fake news using new techniques might not be detected
- **Satire**: Satirical content might be flagged as fake (it's technically not real news)
- **Context**: The system analyzes text only, not images or videos
- **Regional Languages**: Hindi and Gujarati detection is less accurate than English

---

## 🌍 Supported Languages & Regions

### Languages
- 🇬🇧 **English**: Full AI model support
- 🇮🇳 **Hindi (हिंदी)**: Rule-based detection + translation
- 🇮🇳 **Gujarati (ગુજરાતી)**: Rule-based detection + translation

### News Sources
- **Gujarat**: Sandesh, Divya Bhaskar, Gujarat Samachar, Times of India Ahmedabad
- **India**: Times of India, Indian Express, Hindustan Times, The Hindu, NDTV
- **International**: BBC, Reuters, Al Jazeera

### City Coverage
Major cities supported: Ahmedabad, Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata, Pune, Jaipur, Surat, Vadodara, Rajkot, and many more.

---

## 🔒 Privacy & Security

### Your Data is Safe
- Passwords are encrypted using industry-standard hashing
- No news content is stored permanently
- User data is stored locally in MongoDB
- No third-party data sharing

### Security Features
- Email validation
- Password strength requirements
- Secure session management
- Rate limiting to prevent abuse

---

## 🛠️ Technical Architecture

### Frontend
- **HTML/CSS/JavaScript**: Modern, responsive design
- **Bootstrap**: Mobile-friendly interface
- **AJAX**: Real-time updates without page refresh

### Backend
- **Flask**: Python web framework
- **MongoDB**: User authentication database
- **Scikit-learn**: Machine learning models
- **BeautifulSoup**: Web scraping for live news

### Machine Learning
- **Algorithm**: Logistic Regression with TF-IDF vectorization
- **Training**: 50,000+ news articles (real and fake)
- **Features**: Text patterns, word frequencies, linguistic markers
- **Validation**: Cross-validation with 80-20 train-test split

### Deployment
- **Docker**: Containerized deployment
- **Gunicorn**: Production WSGI server
- **Environment Variables**: Secure configuration management

---

## 📊 Project Structure

```
Minor Project New/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
│
├── Backend/
│   └── FND.py                  # Fake News Detection logic
│
├── Frontend/
│   ├── templates/              # HTML pages
│   │   ├── login_new.html
│   │   ├── signup_new.html
│   │   ├── dashboard.html
│   │   ├── truthguard_new.html
│   │   └── threat-map.html
│   └── static/                 # CSS and JavaScript
│       ├── css/
│       └── js/
│
├── Model/                      # Trained ML models
│   ├── model_improved.pkl      # Article model (99.63%)
│   ├── model_headlines.pkl     # Headline model (95.24%)
│   ├── model_hindi.pkl         # Hindi model
│   ├── model_gujarati.pkl      # Gujarati model
│   └── *.csv                   # Training datasets
│
└── tests/                      # Unit tests
    ├── test_app.py
    ├── test_fnd.py
    └── test_validators.py
```

---

## 🧪 Testing

### Run Tests
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Test Coverage
- Unit tests for prediction logic
- Integration tests for API endpoints
- Validation tests for user input

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Found an issue? Create a bug report
2. **Suggest Features**: Have an idea? Share it with us
3. **Improve Accuracy**: Help us collect more training data
4. **Add Languages**: Help us support more Indian languages
5. **Documentation**: Improve this README or add tutorials

---

## 📄 License

This project is developed for educational purposes as part of a Minor Project.

---

## 👥 Team & Credits

### Development Team
- **Project Type**: Minor Project - Fake News Detection
- **Institution**: [Your Institution Name]
- **Academic Year**: [Year]

### Acknowledgments
- Training data from Kaggle datasets
- News sources: Times of India, Indian Express, NDTV, BBC, Reuters, and regional sources
- Open-source libraries: Flask, Scikit-learn, BeautifulSoup

---

## 📞 Support & Contact

### Need Help?
- **Technical Issues**: Check the troubleshooting section below
- **Feature Requests**: Create an issue on the project repository
- **General Questions**: Contact the project administrator

### Troubleshooting

**Problem**: Application won't start
- **Solution**: Make sure MongoDB is running and Python dependencies are installed

**Problem**: Low accuracy on predictions
- **Solution**: Ensure you're using the latest model files (model_improved.pkl)

**Problem**: News feed not loading
- **Solution**: Check your internet connection and firewall settings

**Problem**: Language detection not working
- **Solution**: Make sure the text contains enough content (at least 20 characters)

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Image and video analysis
- [ ] Social media integration (Twitter, Facebook)
- [ ] Browser extension for instant verification
- [ ] Mobile app (Android & iOS)
- [ ] More Indian languages (Tamil, Telugu, Malayalam, Bengali)
- [ ] Fact-checking API for developers
- [ ] Community reporting and feedback
- [ ] Historical fake news database
- [ ] Educational resources about media literacy

---

## 📚 Learn More

### Understanding Fake News
- **What is Fake News?**: Deliberately false information presented as news
- **Types**: Clickbait, propaganda, satire, misleading content, fabricated content
- **Impact**: Influences public opinion, elections, health decisions, and social harmony

### How to Spot Fake News Manually
1. **Check the Source**: Is it from a reputable news organization?
2. **Read Beyond Headlines**: Headlines can be misleading
3. **Check the Date**: Old news can be recirculated as current
4. **Verify with Multiple Sources**: Cross-check with other news outlets
5. **Check Your Biases**: Are you sharing because it confirms your beliefs?
6. **Look for Evidence**: Does it cite credible sources and data?

### Media Literacy Resources
- [UNESCO Media and Information Literacy](https://en.unesco.org/themes/media-and-information-literacy)
- [International Fact-Checking Network](https://www.poynter.org/ifcn/)
- [Google News Initiative](https://newsinitiative.withgoogle.com/)

---

## 🌟 Why TruthGuard Matters

In a world where information travels faster than ever, **truth matters**. TruthGuard empowers individuals to:

- **Make Informed Decisions**: Based on verified information
- **Stop Misinformation**: Before it spreads to others
- **Build Trust**: In digital media and journalism
- **Protect Democracy**: By ensuring informed citizens
- **Promote Critical Thinking**: Encouraging verification before sharing

**Remember**: TruthGuard is a tool to assist you, not replace your judgment. Always think critically and verify important information through multiple sources.

---

## 🙏 Thank You

Thank you for using TruthGuard! Together, we can fight misinformation and build a more informed society.

**Stay Informed. Stay Vigilant. Stay True.**

---

*Last Updated: February 2026*
*Version: 1.0.0*
