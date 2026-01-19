# API Documentation

Complete API reference for the Fake News Detection System.

## Base URL

```
http://localhost:5000
```

## Authentication

The API uses session-based authentication. After successful login, a session cookie is set.

## Rate Limiting

All endpoints are rate-limited to prevent abuse:
- Default: 100 requests per hour per IP
- Login/Signup: 10 requests per minute
- Prediction: 30 requests per minute

## Response Format

All responses are in JSON format:

```json
{
  "message": "Success message",
  "data": {}
}
```

Error responses:

```json
{
  "error": "Error message"
}
```

## Endpoints

### Authentication

#### POST /signup

Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Validation:**
- Email must be valid format
- Password must be at least 6 characters
- Email must be unique

**Response (201):**
```json
{
  "message": "User registered successfully"
}
```

**Error Responses:**
- 400: Invalid email format / Password too short
- 400: Email already exists
- 500: Registration failed

**Rate Limit:** 5 per minute

---

#### POST /login

Authenticate user and create session.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful"
}
```

**Error Responses:**
- 400: Email and password required
- 401: Invalid email or password
- 500: Login failed

**Rate Limit:** 10 per minute

---

#### POST /logout

End user session.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

#### POST /forgot_password

Request password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset link sent to your email"
}
```

**Error Responses:**
- 400: Valid email is required
- 404: Email not found
- 500: Password reset failed

**Rate Limit:** 3 per minute

---

### Prediction

#### POST /predict

Analyze text for fake news detection.

**Request Body:**
```json
{
  "text": "News article text to analyze..."
}
```

**Validation:**
- Text must not be empty
- Text must be at least 10 characters

**Response (200):**
```json
{
  "prediction": "Fake News",
  "confidence": 87.5
}
```

**Fields:**
- `prediction`: Either "Fake News" or "Real News"
- `confidence`: Confidence score (0-100)

**Error Responses:**
- 400: No text provided / Text too short
- 500: Prediction failed
- 503: Model not available

**Rate Limit:** 30 per minute

**Caching:** Results cached for 5 minutes

---

### News Fetching

#### GET /fetch_news

Fetch and analyze real-time news articles.

**Query Parameters:**
- `query` (optional): Search topic (default: "latest")

**Example:**
```
GET /fetch_news?query=technology
```

**Response (200):**
```json
{
  "news": [
    "Article 1 text...",
    "Article 2 text..."
  ],
  "predictions": [
    "Real News",
    "Fake News"
  ]
}
```

**Error Responses:**
- 400: Query parameter required
- 404: No news found
- 500: Failed to fetch news

**Rate Limit:** 10 per minute

**Caching:** Results cached for 5 minutes per query

---

### Utility

#### GET /health

Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "timestamp": "2024-01-19T10:30:00.000Z"
}
```

**No Rate Limit**

---

#### GET /

Render login page.

**Response:** HTML page

---

#### GET /fakenews

Render fake news detection interface.

**Response:** HTML page

**Requires:** Active session

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid credentials |
| 404 | Not Found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Status Codes by Endpoint

| Endpoint | Success | Error Codes |
|----------|---------|-------------|
| /signup | 201 | 400, 500 |
| /login | 200 | 400, 401, 500 |
| /logout | 200 | - |
| /forgot_password | 200 | 400, 404, 500 |
| /predict | 200 | 400, 500, 503 |
| /fetch_news | 200 | 400, 404, 500 |
| /health | 200 | - |

## Examples

### cURL Examples

**Signup:**
```bash
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Login:**
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Predict:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text":"Breaking news: Scientists discover new planet"}'
```

**Fetch News:**
```bash
curl "http://localhost:5000/fetch_news?query=technology" \
  -b cookies.txt
```

### JavaScript Examples

**Signup:**
```javascript
fetch('http://localhost:5000/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Predict:**
```javascript
fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'News article text here...'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Prediction:', data.prediction);
  console.log('Confidence:', data.confidence);
});
```

### Python Examples

**Using requests library:**

```python
import requests

# Signup
response = requests.post('http://localhost:5000/signup', json={
    'email': 'test@example.com',
    'password': 'password123'
})
print(response.json())

# Login
session = requests.Session()
response = session.post('http://localhost:5000/login', json={
    'email': 'test@example.com',
    'password': 'password123'
})
print(response.json())

# Predict
response = session.post('http://localhost:5000/predict', json={
    'text': 'News article text here...'
})
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}%")

# Fetch News
response = session.get('http://localhost:5000/fetch_news', params={
    'query': 'technology'
})
data = response.json()
for article, prediction in zip(data['news'], data['predictions']):
    print(f"{prediction}: {article[:100]}...")
```

## Rate Limit Headers

Responses include rate limit information in headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642598400
```

## CORS

CORS is not enabled by default. For cross-origin requests, configure CORS in the Flask app.

## Webhooks

Currently not supported. Feature planned for future release.

## Versioning

Current API version: v1 (no version prefix in URL)

Future versions will use: `/api/v2/...`

## Support

For API issues or questions:
- Check logs: `app.log`
- GitHub Issues: [repository-url]
- Email: support@example.com

## Changelog

### v1.0.0 (2024-01-19)
- Initial API release
- Authentication endpoints
- Prediction endpoint
- News fetching endpoint
- Health check endpoint

---

**Note:** This API is designed for educational purposes. For production use, implement additional security measures and comprehensive testing.
