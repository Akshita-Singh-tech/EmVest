# Emvest: API Documentation

Base URL: `http://localhost:8000/api/v1`

All responses are serialized in JSON format. Interactive Swagger documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## 1. System & Health

### `GET /api/v1/health`
Checks whether the backend server is operational.

- **Authentication:** None
- **Response:** `200 OK`
```json
{
  "status": "ok"
}
```

---

## 2. Authentication & Profile

### `POST /api/v1/auth/signup` (or `/register`)
Register a new user account.

- **Request Body:**
```json
{
  "email": "investor@emvest.ai",
  "full_name": "Rohan Sharma",
  "password": "SecurePassword123!"
}
```
- **Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "investor@emvest.ai",
    "full_name": "Rohan Sharma",
    "is_active": true,
    "created_at": "2026-11-06T00:00:00"
  }
}
```

### `POST /api/v1/auth/login`
Authenticate with email and password to receive a JWT access token.

- **Request Body:**
```json
{
  "email": "investor@emvest.ai",
  "password": "SecurePassword123!"
}
```
- **Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": { ... }
}
```

### `GET /api/v1/auth/me`
Retrieve details of the currently authenticated user.

- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK`

---

## 3. User Preferences & Personalization

### `GET /api/v1/preferences`
Retrieve the current user's investment preferences and tracking configuration.

- **Authentication:** Optional (defaults to guest preferences if unauthenticated)
- **Response:** `200 OK`
```json
{
  "id": 1,
  "experience_level": "Intermediate",
  "risk_tolerance": "Moderate",
  "investment_horizon": "Medium-Term",
  "tracked_sectors": ["Banking & Financial Services", "Information Technology"],
  "tracked_symbols": ["HDFCBANK", "INFY", "RELIANCE"],
  "sentiment_alert_threshold": 0.75,
  "email_alerts": true,
  "daily_digest": true,
  "digest_time": "08:30",
  "enable_ai_suggestions": true
}
```

### `PUT /api/v1/preferences`
Update user investment preferences.

- **Authentication:** Optional / Bearer
- **Request Body:** Partial or complete `PreferencesUpdate` object.
- **Response:** `200 OK`

---

## 4. Watchlist Management

### `GET /api/v1/watchlist`
List all watchlist items tracked by the user.

- **Response:** `200 OK`
```json
[
  {
    "id": 1,
    "symbol": "TATAMOTORS",
    "name": "Tata Motors Ltd",
    "sector": "Automobile & Auto Ancillary",
    "target_price": 1050.0,
    "notes": "Targeting festive season EV margin expansion",
    "created_at": "2026-11-06T00:00:00"
  }
]
```

### `POST /api/v1/watchlist`
Add a new stock symbol to the watchlist.

- **Request Body:**
```json
{
  "symbol": "TATAMOTORS",
  "name": "Tata Motors Ltd",
  "sector": "Automobile & Auto Ancillary",
  "target_price": 1050.0,
  "notes": "Targeting festive season EV margin expansion"
}
```
- **Response:** `201 Created`

### `DELETE /api/v1/watchlist/{symbol}`
Remove a symbol from the watchlist.

- **Response:** `204 No Content`

---

## 5. News Intelligence & Scrapers

### `GET /api/v1/news`
Retrieve live ingested financial news articles scored by FinBERT.

- **Query Parameters:**
  - `search` (string): Search text across titles and summaries
  - `sentiment` (`Positive` | `Neutral` | `Negative` | `All`)
  - `sector` (string): Filter by industry sector
  - `source` (string): Filter by publisher (LiveMint, ET, etc.)
  - `symbol` (string): Filter by stock symbol
  - `limit` (int, default 50)
  - `offset` (int, default 0)
- **Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "RBI Monetary Policy Committee maintains repo rate at 6.5%",
    "summary": "Central bank keeps policy rate unchanged...",
    "content": "...",
    "source": "LiveMint",
    "url": "https://www.livemint.com/...",
    "published_at": "2026-11-06T00:00:00",
    "sector": "Banking & Financial Services",
    "symbols": ["HDFCBANK", "SBIN", "ICICIBANK"],
    "sentiment": "Positive",
    "sentiment_score": 0.82,
    "sentiment_confidence": 0.94,
    "key_takeaways": ["Repo rate held steady at 6.50%"],
    "market_impact": "Bullish for large private and PSU banks"
  }
]
```

### `POST /api/v1/news/ingest`
Trigger an on-demand RSS ingestion cycle.

- **Response:** `200 OK`
```json
{
  "status": "success",
  "newly_ingested": 2,
  "total_articles": 9
}
```

---

## 6. Financial Sentiment & Market Analytics

### `GET /api/v1/analytics/overview`
Get aggregate market sentiment index, polarity distribution, and total scan stats.

- **Response:** `200 OK`
```json
{
  "composite_score": 0.53,
  "overall_sentiment": "Bullish",
  "total_articles": 7,
  "polarity": {
    "positive": 5,
    "neutral": 1,
    "negative": 1,
    "positive_percentage": 71.4,
    "neutral_percentage": 14.3,
    "negative_percentage": 14.3
  },
  "top_bullish_articles": [ ... ]
}
```

### `GET /api/v1/analytics/sectors`
Get ranked sentiment conviction metrics across all major Indian equity sectors.

- **Response:** `200 OK`

### `GET /api/v1/analytics/company/{symbol}`
Get deep-dive sentiment breakdown, catalysts, and recent news for an equity.

- **Response:** `200 OK`

---

## 7. Grounded AI Assistant (FinBERT RAG)

### `POST /api/v1/chat/query`
Submit a research query to the assistant. The agent retrieves stored articles, calculates FinBERT aggregate sentiment, generates an answer strictly grounded in the database, and returns citations.

- **Request Body:**
```json
{
  "query": "What is the market sentiment for Tata Motors electric vehicles?",
  "session_id": "sess-abc-123"
}
```
- **Response:** `200 OK`
```json
{
  "session_id": "sess-abc-123",
  "role": "assistant",
  "answer": "### Market Intelligence Synthesis for **TATAMOTORS**...\n...",
  "citations": [
    {
      "id": 2,
      "title": "Tata Motors passenger EV registrations climb 18% YoY in October festive sales surge",
      "source": "Economic Times",
      "url": "https://economictimes.indiatimes.com/...",
      "published_at": "2026-11-06 00:00",
      "sentiment": "Positive",
      "sentiment_score": 0.76,
      "symbols": ["TATAMOTORS", "MARUTI"],
      "sector": "Automobile & Auto Ancillary"
    }
  ],
  "suggested_followups": [
    "What are the primary risk factors for TATAMOTORS over the next quarter?",
    "How does TATAMOTORS's FinBERT sentiment compare with its industry peers?"
  ],
  "sentiment_summary": {
    "aggregate_score": 0.76,
    "sentiment_label": "Strongly Bullish",
    "article_count": 1,
    "positive_count": 1,
    "neutral_count": 0,
    "negative_count": 0
  }
}
```

### `GET /api/v1/chat/history/{session_id}`
Retrieve all messages and citation logs for a conversation session.

- **Response:** `200 OK`

### `DELETE /api/v1/chat/history/{session_id}`
Clear chat history for a session.

- **Response:** `200 OK`
```json
{
  "status": "cleared",
  "session_id": "sess-abc-123"
}
```
