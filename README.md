# Fake News Detection System

An AI-powered web application that detects fake news using machine learning and provides real-time news analysis from multiple sources.

## Features

- **AI-Powered Detection**: Uses Naive Bayes classifier with TF-IDF vectorization (94.25% accuracy)
- **Multi-Language Support**: Supports English, Hindi (हिंदी), and Gujarati (ગુજરાતી)
- **Automatic Language Detection**: Detects and translates input automatically
- **Real-Time News Fetching**: Aggregates news from multiple sources (NewsAPI, NewsData.io, web scraping)
- **User Authentication**: Secure login/signup with password hashing
- **Rate Limiting**: Prevents API abuse
- **Caching**: Improves performance for repeated queries
- **Responsive UI**: Modern WhatsApp-inspired chat interface
- **Prediction Logging**: Tracks all predictions for analysis

## Tech Stack

### Backend
- **Flask**: Web framework
- **MongoDB**: User authentication and logging
- **scikit-learn**: Machine learning model
- **BeautifulSoup**: Web scraping

### Frontend
- **HTML/CSS/JavaScript**: Modern responsive UI
- **Font Awesome**: Icons

### ML Model
- **Algorithm**: Multinomial Naive Bayes
- **Vectorization**: TF-IDF (5000 features)
- **Accuracy**: 94.25%
- **Dataset**: 44,898 articles (True.csv + Fake.csv)

## Installation

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- pip

### Setup

1. **Clone the repository**
```bash
cd "CODE/Minor Project New"
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
copy .env.example .env
# Edit .env with your configuration
```

5. **Set up MongoDB**
- Install MongoDB from https://www.mongodb.com/try/download/community
- Start MongoDB service
- Default connection: `mongodb://127.0.0.1:27017/`

6. **Get API Keys** (Optional but recommended)
- NewsAPI: https://newsapi.org/register
- NewsData.io: https://newsdata.io/register

Add keys to `.env`:
```
NEWSAPI_KEY=your_key_here
NEWSDATA_KEY=your_key_here
```

## Running the Application

### Development Mode
```bash
cd Backend
python app.py
```

Visit: http://localhost:5000

### Production Mode
```bash
set FLASK_ENV=production
python Backend/app.py
```

## Project Structure

```
CODE/Minor Project New/
├── Backend/
│   ├── app.py              # Main Flask application
│   └── FND.py              # News fetching & prediction logic
├── Frontend/
│   ├── templates/
│   │   ├── loginpage.html  # Login/Signup page
│   │   └── fakenews.html   # Main detection interface
│   └── Static/
│       ├── css/            # Stylesheets
│       └── js/             # JavaScript files
├── Model/
│   ├── model.pkl           # Trained ML model
│   ├── Final_model_trained.ipynb  # Training notebook
│   ├── True.csv            # Real news dataset
│   └── Fake.csv            # Fake news dataset
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /signup` - Register new user
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /forgot_password` - Password reset request

### Prediction
- `POST /predict` - Analyze text for fake news
  ```json
  {
    "text": "News article text here..."
  }
  ```

### News Fetching
- `GET /fetch_news?query=topic` - Fetch and analyze real-time news

### Utility
- `GET /health` - Health check endpoint

## Usage

### 1. Register/Login
- Create an account or login with existing credentials
- Passwords are securely hashed using PBKDF2-SHA256

### 2. Analyze Text
- Type or paste news article text
- Click send to get instant fake/real prediction
- View confidence score

### 3. Fetch Real-Time News
- Enter a topic (e.g., "Elections", "Technology")
- System fetches news from multiple sources
- Each article is automatically analyzed

## Model Training

The ML model was trained on 44,898 news articles:
- **Real News**: 21,417 articles
- **Fake News**: 23,481 articles

Training process (see `Model/Final_model_trained.ipynb`):
1. Data preprocessing (text cleaning, lowercasing)
2. TF-IDF vectorization (5000 features)
3. Multinomial Naive Bayes classification
4. 80/20 train-test split
5. Achieved 94.25% accuracy

## Security Features

- Password hashing with PBKDF2-SHA256
- Rate limiting on all endpoints
- Input validation and sanitization
- Session management
- Environment variable configuration
- SQL injection prevention (NoSQL)
- XSS protection

## Performance Optimizations

- Response caching (5-minute TTL)
- Model loaded once at startup
- Database connection pooling
- Efficient text preprocessing
- Limited news results (20 articles max)

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
# Windows
net start MongoDB
# Linux
sudo systemctl start mongod
```

### Model Not Loading
- Ensure `Model/model.pkl` exists
- Check file permissions
- Verify scikit-learn version compatibility

### API Rate Limits
- NewsAPI: 100 requests/day (free tier)
- NewsData.io: 200 requests/day (free tier)
- Consider upgrading for production use

## Future Enhancements

- [ ] Email verification for signup
- [ ] Password reset via email
- [ ] User dashboard with prediction history
- [ ] Advanced ML models (BERT, LSTM)
- [ ] Multi-language support
- [ ] Browser extension
- [ ] Mobile app
- [ ] Fact-checking integration
- [ ] Source credibility scoring
- [ ] Social media integration

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Dataset: Kaggle Fake News Detection Dataset
- Icons: Font Awesome
- Framework: Flask
- ML Library: scikit-learn

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is an educational project. For production use, consider additional security measures, scalability improvements, and comprehensive testing.
