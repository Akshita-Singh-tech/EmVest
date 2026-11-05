# Emvest: Architecture Specification

## 1. System Overview

Emvest is an agentic investment intelligence platform designed to ingest news and market signals, evaluate market sentiment using specialized financial NLP models (FinBERT), present actionable analytics, and provide conversational research via an AI assistant.

```
┌────────────────────────────────────────────────────────┐
│                      Client Layer                      │
│        React 19 + TypeScript + Vite + Tailwind v4      │
└───────────────────────────▲────────────────────────────┘
                            │ HTTP / JSON (REST)
┌───────────────────────────▼────────────────────────────┐
│                      Backend Layer                     │
│               FastAPI (Python 3.11+ / Uvicorn)         │
│  ┌───────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │  Health API   │ │ Watchlists API │ │  Analytics   │ │
│  └───────────────┘ └────────────────┘ └──────────────┘ │
│  ┌───────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │ AI Assistant  │ │ Sentiment API  │ │ Scrapers     │ │
│  └───────────────┘ └────────────────┘ └──────────────┘ │
└─────────────▲─────────────────────────────▲────────────┘
              │                             │
┌─────────────▼───────────────┐ ┌───────────▼────────────┐
│      Storage Layer          │ │    Ingestion & NLP     │
│   PostgreSQL + SQLAlchemy   │ │  RSS / Scrapers,       │
│        + Alembic            │ │  FinBERT Sentiment,    │
│                             │ │  LLM Provider APIs     │
└─────────────────────────────┘ └────────────────────────┘
```

---

## 2. Technology Stack

### Frontend
- **Framework:** React 19 with TypeScript 5.8+ / 6.0
- **Build Tool:** Vite 8.3+ with `@tailwindcss/vite`
- **Styling:** Tailwind CSS v4
- **Routing:** React Router 7
- **Linting:** ESLint 10

### Backend
- **Framework:** FastAPI
- **Language & Runtime:** Python 3.11+ running inside Conda environment `emvest`
- **Configuration:** `pydantic-settings` with `.env` support
- **Testing:** Pytest + HTTPX (`TestClient`)
- **Server:** Uvicorn with standard extras

### Persistence & Data (Phase 6+)
- **Database:** PostgreSQL (Dockerized or local instance)
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic

### Intelligence & Processing (Phase 7 & 8)
- **Sentiment Model:** FinBERT (HuggingFace Transformers / PyTorch)
- **Scraping:** RSS feeds, BeautifulSoup / Trafilatura
- **LLM Layer:** Configurable LLM API provider for RAG and contextual financial reasoning

---

## 3. Directory Layout & Module Responsibilities

### Backend Modules (`backend/app/`)
- **`api/`**: HTTP route controllers and endpoint routers (versioned under `/api/v1`).
- **`core/`**: Application configuration, settings, security, and global constants.
- **`models/`**: SQLAlchemy database model definitions.
- **`schemas/`**: Pydantic input/output schemas for API validation and serialization.
- **`database/`**: Database engine setup, session makers, and migration scripts.
- **`services/`**: Core business logic decoupled from HTTP transport.
- **`chatbot/`**: Prompt templates, context building, and LLM orchestration.
- **`analytics/`**: Financial calculations, metrics aggregation, sector analytics.
- **`sentiment/`**: FinBERT model loading, inference pipelines, score weighting.
- **`scrapers/`**: Asynchronous RSS feed readers and publisher scrapers.
- **`twitter/`**: Optional X/Twitter ingestion module (behind feature toggle).

### Frontend Modules (`frontend/src/`)
- **`components/`**:
  - `ui/`: Atomic elements (buttons, inputs, badges, cards, spinners).
  - `layout/`: Top navigation, sidebar, page wrappers, responsive containers.
  - `common/`: Empty states, error boundaries, confirmation modals.
- **`pages/`**: Route views (Dashboard, Analytics, News Feed, Watchlists, AI Chat, Settings).
- **`services/`**: Typed API clients (`api.ts`).
- **`styles/`**: Global stylesheet importing Tailwind CSS v4 (`styles/index.css`).
- **`hooks/`**: Custom reusable React hooks.
- **`types/`**: Shared TypeScript interfaces and domain types.

---

## 4. Security & Best Practices

1. **Environment Variables:** All secrets and environment-specific configs are managed via `.env` and typed in `app.core.config.Settings`.
2. **CORS:** Strict origin policies configured in FastAPI (`CORSMiddleware`).
3. **Reproducibility:** Dependencies tracked in `requirements.txt` (to be pinned prior to production) and `package-lock.json`.

