# Emvest: Comprehensive Architecture Specification

## 1. System Overview

Emvest is an agentic investment intelligence and financial NLP platform built for Indian equities and market sectors. It combines real-time multi-publisher RSS ingestion, financial sentiment analysis with FinBERT, interactive portfolio and sector analytics, and a grounded conversational AI assistant with verifiable citations.

```mermaid
flowchart TD
    subgraph Client ["Frontend Layer (React 19 + TypeScript + Vite + Tailwind v4)"]
        UI_Shell["UI Shell (Sidebar, Navbar, AppLayout)"]
        Pages["7 Routed Views (Dashboard, Analytics, News, Watchlist, Chat, Profile, Settings)"]
        Recharts["Interactive Analytics Visuals (Area, Bar, Donut)"]
        ApiClient["Typed API Services (REST with Local Fallback)"]
    end

    subgraph Backend ["Backend Layer (FastAPI + Python 3.11)"]
        Router["Versioned API Router (/api/v1)"]
        AuthModule["JWT Authentication & Password Security (Bcrypt)"]
        PrefModule["User Preferences & Watchlist Controllers"]
        NewsModule["News Feed & Ingestion Endpoints"]
        AnalyticsModule["Sector & Composite Analytics Engine"]
        ChatModule["Grounded AI Research Assistant (ChatAgent)"]
    end

    subgraph Pipeline ["Intelligence & Ingestion Pipeline"]
        Scrapers["RSS Scrapers (ET, LiveMint, Business Standard, Moneycontrol)"]
        Twitter["Twitter / X Ingestion (Flag Gated)"]
        FinBERT["FinBERT NLP Worker & Polarity Classifier"]
        Seeder["Startup Ingestion & Deduplication"]
    end

    subgraph Storage ["Storage Layer"]
        DB[(PostgreSQL / SQLite via SQLAlchemy 2.0)]
        Migrations["Alembic Migrations Engine"]
    end

    UI_Shell --> Pages
    Pages --> ApiClient
    ApiClient -->|HTTP / JSON| Router
    Router --> AuthModule
    Router --> PrefModule
    Router --> NewsModule
    Router --> AnalyticsModule
    Router --> ChatModule

    NewsModule --> Ingestion
    Pipeline -->|Normalized Records| Storage
    AuthModule --> DB
    PrefModule --> DB
    NewsModule --> DB
    AnalyticsModule --> DB
    ChatModule --> DB
```

---

## 2. Technology Stack

### Frontend Architecture
- **Framework:** React 19 (`react`, `react-dom`)
- **Language:** TypeScript 5.8+ / 6.0
- **Build Tool:** Vite 8.3.6 with `@tailwindcss/vite`
- **Styling:** Tailwind CSS v4 (Modern CSS variables, OKLCH color space, zero-config utility classes)
- **Routing:** React Router 7 (`react-router-dom`)
- **Data Visualization:** Recharts 2.15 (ResponsiveContainer, AreaChart, BarChart, PieChart)
- **Linting & Quality:** ESLint 10 with `typescript-eslint`

### Backend Architecture
- **Web Framework:** FastAPI (Asynchronous ASGI framework with OpenAPI / Swagger UI auto-generation)
- **Runtime:** Python 3.11+ running inside Conda environment `emvest`
- **Configuration:** `pydantic-settings` (v2) with `.env` file loading
- **Data Serialization:** Pydantic v2 schemas (`model_config = ConfigDict(from_attributes=True)`)
- **Database ORM:** SQLAlchemy 2.0 (Declarative Base, Scoped Sessions)
- **Database Engine:** SQLite for zero-setup local dev (`emvest.db`) / PostgreSQL for production
- **Migrations:** Alembic
- **Security:** `bcrypt` native password hashing + `PyJWT` authentication
- **Test Framework:** Pytest 8.4 + HTTPX (`TestClient`)

---

## 3. Database Schema & Entity Relationships

```mermaid
erDiagram
    USERS ||--|| USER_PREFERENCES : "has"
    USERS ||--o{ WATCHLIST_ITEMS : "tracks"
    USERS ||--o{ CHAT_MESSAGES : "authors"

    USERS {
        int id PK
        string email UK
        string full_name
        string hashed_password
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    USER_PREFERENCES {
        int id PK
        int user_id FK
        string experience_level
        string risk_tolerance
        string investment_horizon
        json tracked_sectors
        json tracked_symbols
        float sentiment_alert_threshold
        boolean email_alerts
        boolean daily_digest
        string digest_time
        boolean enable_ai_suggestions
        datetime updated_at
    }

    WATCHLIST_ITEMS {
        int id PK
        int user_id FK
        string symbol
        string name
        string sector
        float target_price
        text notes
        datetime created_at
    }

    ARTICLES {
        int id PK
        string title
        text summary
        text content
        string source
        string url UK
        datetime published_at
        string sector
        json symbols
        string sentiment
        float sentiment_score
        float sentiment_confidence
        json key_takeaways
        string market_impact
        datetime created_at
    }

    CHAT_MESSAGES {
        int id PK
        string session_id
        int user_id FK
        string role
        text content
        json citations
        datetime created_at
    }
```

---

## 4. Pipeline & Ingestion Architecture

```mermaid
sequenceDiagram
    participant S as RSS / Publisher Feeds
    participant P as Ingestion Service
    participant FB as FinBERT NLP Worker
    participant DB as Database (Articles)
    participant UI as React Client

    S->>P: Fetch RSS XML feeds (ET, Mint, BS, Moneycontrol)
    P->>P: Parse XML, normalize publication timestamps & URLs
    P->>DB: Check URL deduplication filter
    alt Article is new
        P->>FB: Pass title, summary & body
        FB->>FB: Run dictionary + context scoring
        FB-->>P: Return polarity, confidence & sentiment score
        P->>DB: Save Article with FinBERT sentiment & symbols
    else Article exists
        P->>P: Skip duplicate
    end
    UI->>DB: Fetch /api/v1/news (Filter by sector, sentiment, query)
    DB-->>UI: Return live verified article stream
```

---

## 5. Grounded AI Assistant & LLM Layer

The AI assistant operates on a hybrid architecture: grounded LLM generation when configured with a provider API key, with an automated fallback to the deterministic financial reasoning engine.

```mermaid
flowchart TD
    UserQuery["User Chat Query"] --> Agent["ChatAgent.process_query"]
    Agent --> Memory["Retrieve Session Memory (ChatMessage)"]
    Agent --> Retrieval["Database Retrieval (Article Table)"]
    Retrieval --> Factory{"get_provider()"}
    Factory -->|None / Missing Key / Deterministic| Fallback["Rule-Based Intent Engine"]
    Factory -->|Active Provider| LLM["LLM Provider (Gemini / OpenAI via httpx)"]
    LLM -->|LLMError / Timeout / Empty| Fallback
    LLM -->|Success| Grounded["Grounded Response with Verified [n] Citations"]
    Fallback --> DBWrite["Persist Turn to Database"]
    Grounded --> DBWrite
    DBWrite --> Client["ChatQueryResponse (Answer + Citations)"]
```

### Provider Wrapper (`app/chatbot/llm/`)
- **Abstract Base (`base.py`):** `LLMProvider` interface defining `generate(system_prompt, user_prompt, *, timeout=15.0) -> str` and the sanitized `LLMError` exception.
- **Gemini Provider (`gemini_provider.py`):** Communicates directly with Google AI Studio `v1beta/models/{model}:generateContent` using `httpx`. Headers carry `x-goog-api-key`. System instructions use the root-level `systemInstruction` field. Model defaults to `gemini-2.5-flash` via `settings.gemini_model`.
- **OpenAI Provider (`openai_provider.py`):** Communicates directly with OpenAI `v1/chat/completions` using `httpx`. Authorization uses `Bearer {api_key}`. Model defaults to `gpt-4o-mini` via `settings.openai_model`.
- **Factory (`factory.py`):** Resolves provider based on `settings.default_llm_provider`:
  - `"auto"`: Returns `GeminiProvider` if `gemini_api_key` is set, else `OpenAIProvider` if `openai_api_key` is set, else `None`.
  - `"deterministic"`: Always returns `None`.
  - `"gemini"` / `"openai"`: Selects specific provider if its key is configured, else returns `None`.

### Grounded Prompting & Untrusted Data Boundary
- **Sources Delimitation:** Database articles are wrapped inside `<sources>` tags with labeled identifiers `[1]`, `[2]`, etc., including publisher, timestamp, sentiment label, and summary.
- **Prompt Injection Defense:** System instructions explicitly require the model to treat all text inside `<sources>` as untrusted data and strictly ignore any adversarial instructions or prompt injections inside source bodies.
- **Citation Filtering:** Citations in the final response are matched to the `[n]` references actually used in the generated text. Any non-existent `[n]` references are dropped.
- **Disclaimer Enforcement:** The LLM prompt enforces ending every generated analysis with a one-line "not financial advice" note.

### Reliability & Error Isolation
- **Timeout & Retry:** Network calls enforce a 15.0-second timeout with one automatic retry on timeouts or 5xx server errors.
- **Clean Fallback:** If `LLMError` or an empty response occurs, the system logs a field-free warning (`"LLM generation failed, falling back to rule-based answer"`) with zero sensitive parameters and delivers the deterministic rule-based response.

### Verification Scope (Live vs. Unit-Tested)
- **Unit-Tested:** Factory provider selection, missing key handling, request formatting, 5xx retry logic (mocked via `httpx.MockTransport`), agent citation filtering, prompt injection defense, and rule-based fallback.
- **Live Integration:** Not marked as live-tested until the operator runs `python scripts/check_llm.py` with an authentic API key and confirms live response generation.

---

## 6. Sentiment Engine Specification

The sentiment engine (`FinBertSentimentWorker` in `app/sentiment/finbert_worker.py`) is a lightweight, financial-lexicon scoring service. It evaluates financial news headlines and article bodies using categorized financial terminology (`BULLISH_KEYWORDS` and `BEARISH_KEYWORDS`), generating structured confidence metrics, directional market impact takeaways, and normalized polarity scores on a `-1.0` to `+1.0` scale. It does not run heavy neural transformer model weights locally.

---

## 6. Security & Credential Boundary

- **API Keys:** External LLM and Twitter credentials (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `TWITTER_BEARER_TOKEN`) reside strictly in backend environment variables. The client never receives or transmits API keys.
- **Passwords:** Passwords hashed with salted bcrypt rounds (12 passes) and verified via constant-time checks. Passwords truncated to 72 bytes to prevent bcrypt wraparound attacks.
- **Tokens:** JWTs issued with standard claims (`sub`, `user_id`, `exp`) and validated via FastAPI OAuth2 dependency injection.
- **CORS Protection:** Configured with whitelisted development and production client origins.
- **Database Safety:** SQLAlchemy ORM parameterization guarantees protection against SQL injection.
