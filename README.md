# Emvest

> **AI-Powered Stock Market Intelligence & Agentic Investment Research**

Emvest is a modern financial intelligence and investment research platform that combines real-time market data ingestion, sentiment analysis, agentic AI assistance, and interactive portfolio analytics for Indian and global equities.

---

## Architecture Overview

- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS v4 + React Router
- **Backend:** FastAPI (Python 3.11+) + Pydantic v2 + Uvicorn
- **Database & Persistence (Upcoming Phase 6):** PostgreSQL + SQLAlchemy + Alembic
- **Intelligence & NLP (Upcoming Phases 7 & 8):** FinBERT sentiment analysis, RSS / news scrapers, and LLM-powered retrieval assistant

---

## Getting Started

### Prerequisites

- **Node.js:** v20+ (`node -v`)
- **Python:** 3.11+ via Conda (`conda --version`)
- **Git:** Installed and configured

---

### Backend Setup

1. **Activate the Conda environment:**
   ```bash
   conda activate emvest
   ```

2. **Navigate to the backend directory and install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run the backend development server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend API will be available at `http://localhost:8000`.
   API Documentation (Swagger UI): `http://localhost:8000/docs`.

4. **Run tests:**
   ```bash
   python -m pytest
   ```

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

4. **Build and lint:**
   ```bash
   npm run lint
   npm run build
   ```

---

## Project Structure

```text
emvest/
├── docs/                   # Project documentation, architecture, logs
│   ├── architecture.md
│   ├── api-documentation.md
│   └── development-log.md
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/            # API route controllers
│   │   ├── core/           # Configuration and settings
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── database/       # DB session and migrations
│   │   ├── services/       # Business logic
│   │   ├── chatbot/        # AI assistant service
│   │   ├── analytics/      # Financial metrics and calculations
│   │   ├── sentiment/      # FinBERT NLP pipelines
│   │   ├── scrapers/       # RSS & news scrapers
│   │   └── twitter/        # X/Twitter data ingestion
│   ├── tests/              # Pytest test suite
│   ├── requirements.txt
│   └── main.py             # FastAPI entrypoint
├── frontend/               # Vite + React 19 application
│   ├── src/
│   │   ├── components/     # UI, Layout, and Common components
│   │   ├── pages/          # Routed pages
│   │   ├── services/       # API clients
│   │   ├── styles/         # Global styles & Tailwind
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── .env.example            # Environment variables template
├── .gitignore
└── README.md
```

---

## Roadmap

- [x] **Phase 1: Project Foundation** (Backend scaffolding, Conda 3.11 env, FastAPI health API, Vite + React 19 + Tailwind v4 frontend, verification)
- [x] **Phase 2: UI Shell** (Responsive layout, sidebar, navbar, 7 routed pages, shared UI primitives: Card, Badge, EmptyState, Button)
- [ ] **Phase 3: Analytics UI** (Recharts, sentiment charts, company/sector views)
- [ ] **Phase 4: News Intelligence UI** (Live feed, article cards, filters, detail view)
- [ ] **Phase 5: Personalization UI** (Profile, watchlists, sector selection, preferences)
- [ ] **Phase 6: Backend & DB** (PostgreSQL, SQLAlchemy, Alembic, auth, preferences API)
- [ ] **Phase 7: Data Pipeline** (RSS/scrapers, FinBERT sentiment worker, analytics endpoints)
- [ ] **Phase 8: AI Assistant** (Retrieval, context building, LLM service, source citations)
- [ ] **Phase 9: Integration & E2E Testing** (Full end-to-end testing, security review, polish)

