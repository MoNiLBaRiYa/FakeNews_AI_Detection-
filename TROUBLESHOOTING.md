# Troubleshooting Guide

## "Failed to fetch news" Error

If you see the error "Failed to fetch news. Please try again." in the application, follow these steps:

### 1. Check API Keys

The application requires valid API keys from NewsAPI and NewsData.io.

**Verify your `.env` file contains valid API keys:**

```bash
# Open .env file and check these lines:
NEWSAPI_KEY=your-actual-key-here  # NOT the placeholder!
NEWSDATA_KEY=your-actual-key-here  # NOT the placeholder!
```

### 2. Get Free API Keys

If you don't have API keys yet:

1. **NewsAPI**: Visit https://newsapi.org/register
   - Sign up for a free account
   - Copy your API key
   - Paste it in `.env` as `NEWSAPI_KEY=your-key-here`

2. **NewsData.io**: Visit https://newsdata.io/register
   - Sign up for a free account
   - Copy your API key
   - Paste it in `.env` as `NEWSDATA_KEY=your-key-here`

### 3. Restart the Application

After updating the `.env` file:

1. Stop the Flask server (Ctrl+C)
2. Restart it:
   ```bash
   python Backend/app.py
   # or
   python app.py
   ```

### 4. Check the Console Output

When the app starts, you should see:
```
✓ Loaded .env from: C:\path\to\your\.env
✓ API keys configured successfully
```

If you see warnings about placeholder keys, your `.env` file is not being loaded correctly.

### 5. Verify API Key Status

Check the application logs (`app.log`) for errors like:
- `401 Unauthorized` - Invalid or missing API key
- `429 Too Many Requests` - Rate limit exceeded (wait or upgrade plan)
- `Connection timeout` - Network issues

### 6. Test Individual News Sources

The app fetches from multiple sources:
- Web scraping (Times of India, Indian Express, Hindustan Times)
- NewsAPI
- NewsData.io

If one source fails, others should still work. Check `app.log` to see which sources are failing.

### Common Issues

**Issue**: "NEWSAPI_KEY not configured or using placeholder"
**Solution**: Replace `your-newsapi-key-here` with your actual API key in `.env`

**Issue**: News fetching works sometimes but not always
**Solution**: Free API plans have rate limits. Wait a few minutes or upgrade your plan.

**Issue**: `.env` file changes not taking effect
**Solution**: Make sure you restart the Flask server after editing `.env`

### Still Having Issues?

1. Check `app.log` for detailed error messages
2. Verify MongoDB is running: `mongod --version`
3. Test the health endpoint: `curl http://localhost:5000/health`
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
