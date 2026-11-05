# Emvest: API Documentation

Base URL: `http://localhost:8000/api/v1`

All responses are serialized in JSON format. Interactive Swagger documentation is available at `/docs` and ReDoc at `/redoc`.

---

## Health Check API

### `GET /api/v1/health`
Checks whether the backend server is operational and responsive.

- **Tags:** `health`
- **Authentication:** None
- **Query Parameters:** None

#### Response:
- **Status Code:** `200 OK`
- **Content-Type:** `application/json`
- **Schema:**
  ```json
  {
    "status": "string"
  }
  ```
- **Example Response:**
  ```json
  {
    "status": "ok"
  }
  ```

#### Example Usage:
```bash
curl -i http://localhost:8000/api/v1/health
```

---

## Planned API Roadmap

### Phase 6: Preferences & Watchlists
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/preferences` - Get user portfolio and watchlist preferences
- `PUT /api/v1/preferences` - Update user tracking preferences
- `GET /api/v1/watchlists` - Get user watchlists
- `POST /api/v1/watchlists` - Add stock symbol to watchlist

### Phase 7: Analytics & Sentiment
- `GET /api/v1/analytics/overview` - Aggregate market intelligence
- `GET /api/v1/analytics/company/{symbol}` - Specific company metrics
- `GET /api/v1/news/feed` - Live ingested articles with FinBERT sentiment scores
- `GET /api/v1/sentiment/trends` - Daily and weekly sentiment trajectories

### Phase 8: AI Assistant
- `POST /api/v1/chat/query` - Conversational query to the financial intelligence agent
- `GET /api/v1/chat/history` - Retrieve prior conversation threads
