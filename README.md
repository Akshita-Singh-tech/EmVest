# Emvest — Financial Intelligence & Investment Research Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Emvest** is a comprehensive, production-grade financial intelligence and agentic investment research platform designed specifically for the **Indian Equities Market (NSE / BSE)** and global macroeconomic tracking.

It integrates live multi-source RSS scraping, a financial lexicon sentiment engine, dynamic sector/equity analytics, persistent user preferences, and a grounded AI financial research assistant with provider-backed LLM generation (Gemini / OpenAI) and automatic rule-based fallback.

---

## 🌟 Key Features

### 1. 📰 Real-Time Multi-Source Market Ingestion
- Actively ingests live market headlines and company news from **The Economic Times**, **LiveMint**, and **Moneycontrol**.
- Automatic ticker extraction for **60+ Indian equities** (`RELIANCE`, `TCS`, `HDFCBANK`, `INFY`, `TATAMOTORS`, `SBIN`, `ITC`, `TITAN`, `BAJFINANCE`, etc.).
- Categorizes articles across 10 core Indian sectors (*Banking & Financial Services, IT, Automobile, Energy & Oil, Pharma, FMCG, Metals, Infrastructure, Telecom, Macro*).
- Live on-demand scrapers with immediate database persistence into SQLite (`emvest.db`).

### 2. 🧠 Neural FinBERT Sentiment Engine
- Evaluates real-time financial sentiment with neural inference using Hugging Face **`ProsusAI/finbert`** (BERT fine-tuned on Financial PhraseBank).
- Computes softmax probability distributions across `Positive`, `Neutral`, and `Negative` categories, mapped to continuous scores from `-1.0` to `+1.0` and calibrated confidence metrics.
- Leverages Apple Silicon **MPS** (Metal Performance Shaders) / CUDA / CPU hardware acceleration with token truncation (512 tokens).
- Automatically extracts bulleted **Key Investment Takeaways** and directional **Market Impact** commentary with confidence tags.
- Includes a resilient heuristic fallback ensuring uninterrupted operation in offline or resource-constrained environments.

### 3. 🤖 Grounded AI Financial Assistant (LLM Layer + Rule-Based Fallback)
- **Dual-Mode Generation:** Powered by a direct HTTP LLM provider layer (**Google Gemini** or **OpenAI**) with seamless fallback to an extensive deterministic financial reasoning engine.
- **Provider Wrapper (`app/chatbot/llm/`):** Vendor-independent implementation using `httpx` (no bulky SDKs). Features configurable models (`gemini-2.5-flash`, `gpt-4o-mini`), 15s timeout, one retry on 5xx or timeout, and sanitized exception handling.
- **Grounded & Untrusted Data Defense:** Formats retrieved database articles inside delimited `<sources>` blocks, instructs the LLM to ignore adversarial prompt injections inside articles, and filters citations to match only the sources actually referenced (`[1]`, `[2]`).
- **SEBI / Non-Financial Advice Protection:** Enforces ending every response with a one-line "not financial advice" note.
- **Coverage:** Covers **60+ equities**, 12 sector theses, 35+ fundamental and technical metrics (P/E, ROCE, RSI, MACD, EBITDA margins), and capital allocation blueprints.

### 4. 📊 Real-Time Sentiment Intelligence & Analytics Dashboard
- **Composite Sentiment Index**: Dynamically calculated across all ingested articles.
- **Sentiment Trajectory Chart**: Interactive Recharts area chart tracking market drift over time.
- **Polarity Donut**: Proportional split of Bullish, Neutral, and Bearish market sentiments.
- **Sector Comparison Bar Chart**: Relative momentum and sentiment rankings across all 10 Indian industry sectors.
- **Company Deep Dive**: Ticker-level metrics, primary catalysts, and recent indexed news.

### 5. ⚙️ Personalization & Watchlist
- Persistent investor profile tracking (Experience level, Risk tolerance, Tracked symbols, Tracked sectors).
- Filter the entire news feed by personal watchlist tickers and sectors with one click.
- Full REST API synchronization between SQLite database and frontend state.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph Data Sources
        ET["The Economic Times"]
        LM["LiveMint"]
        MC["Moneycontrol"]
    end

    subgraph Backend [FastAPI Backend (:8008)]
        Ingest["RSS Ingestion & Scraper Pipeline"]
        Sent["Financial Sentiment Engine"]
        Agent["ChatAgent (RAG Engine)"]
        LLM["LLM Layer (Gemini / OpenAI / Fallback)"]
        DB[(SQLite Database: emvest.db)]
        API["REST Endpoints /api/v1"]
    end

    subgraph Frontend [React 19 + Vite (:5173)]
        News["News Intelligence Feed"]
        Analytics["Recharts Sentiment Dashboard"]
        Chat["AI Assistant & Chat History"]
        Watchlist["Watchlist & Preferences"]
    end

    ET --> Ingest
    LM --> Ingest
    MC --> Ingest
    Ingest --> Sent
    Sent --> DB
    DB --> API
    API --> Agent
    Agent --> LLM
    API --> News
    API --> Analytics
    API --> Chat
    API --> Watchlist
```

---

## ⚙️ Environment Variables & LLM Configuration

Configure environment variables in `.env` (or pass via environment):

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_LLM_PROVIDER` | `auto` | Provider mode: `auto` (Gemini if key set, else OpenAI, else fallback), `gemini`, `openai`, or `deterministic` |
| `GEMINI_API_KEY` | *(None)* | Google AI Studio API key (kept strictly on backend) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `OPENAI_API_KEY` | *(None)* | OpenAI API key (kept strictly on backend) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |

> **Privacy & Security Note:** API keys are read solely from backend environment variables and are never transmitted to the frontend, logged, or included in API error responses.

---

## 🧪 Testing Scope (Unit vs. Live Integration)

- **Unit Tests:** Request/response payloads, 5xx retries, timeout handling, and prompt injection defense are fully unit-tested using `httpx.MockTransport` and faked providers (do not require an external API key or network access).
- **Live Integration Check:** Use the dedicated script `backend/scripts/check_llm.py` to make a live test call with an active provider key:
  ```bash
  export GEMINI_API_KEY="your-key-here"
  cd backend && python scripts/check_llm.py
  ```
    LM --> Ingest
    MC --> Ingest
    Ingest --> FinBERT
    FinBERT --> DB
    DB --> API
    API --> Agent
    API --> News
    API --> Analytics
    API --> Chat
    API --> Watchlist
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Node.js** v20+ (`node -v`)
- **Python** 3.11+ (`python3 --version`)
- **Git**

---

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/emvest.git
cd emvest
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Seed / scrape real live Indian market news immediately
python ingest_real_news.py

# Start the FastAPI server on port 8008
uvicorn main:app --port 8008 --reload
```
The backend API will run at `http://localhost:8008`.
Interactive Swagger API Docs: `http://localhost:8008/docs`

---

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Open `http://localhost:5173` in your browser.
Vite reverse-proxies `/api` requests directly to `http://127.0.0.1:8008/api/v1`.

---

### 4. Running Tests & Verifications

```bash
# Run Backend Test Suite (24 tests)
cd backend
PYTHONPATH=. .venv/bin/pytest

# Run Frontend Lint & Typecheck Build
cd ../frontend
npm run lint
npm run build
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status check |
| `GET` | `/api/v1/news` | List indexed market articles with sentiment filters, sectors, and symbols |
| `POST` | `/api/v1/news/ingest` | Trigger live multi-publisher RSS ingestion |
| `GET` | `/api/v1/analytics/overview` | Composite sentiment index, polarity percentages, and trajectory |
| `GET` | `/api/v1/analytics/sectors` | Comparative sentiment rankings for Indian industry sectors |
| `GET` | `/api/v1/analytics/company/{symbol}` | Equity-specific sentiment score, catalysts, and recent articles |
| `POST` | `/api/v1/chat/query` | Ask AI Copilot with multi-turn conversation memory |
| `GET` | `/api/v1/chat/history/{session_id}` | Retrieve full conversation trajectory |
| `GET` | `/api/v1/preferences` | Retrieve persistent investor preferences |
| `PUT` | `/api/v1/preferences` | Update investor risk tolerance and tracked symbols |
| `GET` | `/api/v1/watchlist` | Get user watchlist items |
| `POST` | `/api/v1/watchlist` | Add a stock symbol to watchlist |
| `DELETE` | `/api/v1/watchlist/{symbol}` | Remove a stock symbol from watchlist |

---

## 📂 Project Structure

```text
emvest/
├── backend/                        # FastAPI Python backend
│   ├── app/
│   │   ├── api/                    # REST routes (news, analytics, chat, preferences, watchlist)
│   │   ├── chatbot/                # Multi-intent financial AI reasoning engine
│   │   ├── database/               # SQLAlchemy DB engine & session
│   │   ├── models/                 # ORM models (Article, ChatSession, UserPreferences, Watchlist)
│   │   ├── scrapers/               # Multi-source RSS feed parsers
│   │   ├── sentiment/              # FinBERT NLP sentiment scoring worker
│   │   └── services/               # Ingestion pipeline & business logic
│   ├── tests/                      # Pytest automated test suite
│   ├── ingest_real_news.py         # Standalone live scraping script
│   ├── requirements.txt
│   └── main.py                     # Server entrypoint
├── frontend/                       # React 19 + TypeScript frontend
│   ├── src/
│   │   ├── components/             # Reusable UI primitives, charts, layouts
│   │   ├── pages/                  # NewsPage, AnalyticsPage, ChatbotPage, WatchlistPage, ProfilePage
│   │   ├── services/               # API clients & store synchronization
│   │   └── types/                  # Strict TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts              # Vite config with API reverse proxy
├── .gitignore
├── .env.example
└── README.md
```

---

## 📄 License
This project is licensed under the MIT License.
