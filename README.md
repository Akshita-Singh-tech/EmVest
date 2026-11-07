# Emvest — AI-Powered Stock Market Intelligence & Agentic Investment Research

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FinBERT](https://img.shields.io/badge/NLP-FinBERT-FF6F00?style=flat)](https://huggingface.co/ProsusAI/finbert)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Emvest** is a comprehensive, production-grade financial intelligence and agentic investment research platform designed specifically for the **Indian Equities Market (NSE / BSE)** and global macroeconomic tracking.

It integrates live multi-source RSS scraping, an NLP FinBERT sentiment engine, dynamic sector/equity analytics, persistent user preferences, and a ChatGPT-style multi-turn financial research assistant.

---

## 🌟 Key Features

### 1. 📰 Real-Time Multi-Source Market Ingestion
- Actively ingests live market headlines and company news from **The Economic Times**, **LiveMint**, and **Moneycontrol**.
- Automatic ticker extraction for **60+ Indian equities** (`RELIANCE`, `TCS`, `HDFCBANK`, `INFY`, `TATAMOTORS`, `SBIN`, `ITC`, `TITAN`, `BAJFINANCE`, etc.).
- Categorizes articles across 10 core Indian sectors (*Banking & Financial Services, IT, Automobile, Energy & Oil, Pharma, FMCG, Metals, Infrastructure, Telecom, Macro*).
- Live on-demand scrapers with immediate database persistence into SQLite (`emvest.db`).

### 2. 🧠 FinBERT Financial Sentiment Engine
- Evaluates real-time financial sentiment with confidence scores (`Positive`, `Neutral`, `Negative` on a `-1.0` to `+1.0` scale).
- Extracts bulleted **Key Investment Takeaways** and classifies directional **Market Catalysts**.
- Eliminates mock data — powers all UI feeds directly from verified publisher articles.

### 3. 🤖 ChatGPT-Style Multi-Turn AI Financial Assistant
- Multi-turn conversational memory with persistent session storage and clear-session management.
- Covers **60+ equities**, 12 sector theses, 35+ fundamental and technical metrics (P/E, ROCE, RSI, MACD, EBITDA margins).
- Pre-engineered capital allocation blueprints (₹10,000, ₹50,000, ₹1 Lakh, ₹10 Lakhs) across Conservative, Balanced, and Aggressive profiles.
- Provides grounded source citations with direct links to real news articles.

### 4. 📊 Real-Time Sentiment Intelligence & Analytics Dashboard
- **Composite FinBERT Index**: Dynamically calculated across all ingested articles.
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
        FinBERT["FinBERT NLP Sentiment Engine"]
        Agent["Chatbot & Financial Intelligence Agent"]
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
