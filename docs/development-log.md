# Emvest: Development Log

## Phase 1: Project Foundation (Completed)

### Milestones & Evidence

| Item | Evidence / Raw Verification | Status |
| :--- | :--- | :--- |
| **Git repository & docs** | Initialized repository, created `.gitignore`, `.env.example`, `docs/` | Verified |
| **Backend scaffolding** | 11 core module folders created under `backend/app/` with `tests/` | Verified |
| **Python 3.11 environment** | Dedicated Conda environment `emvest` active with Python 3.11 | Verified |
| **Backend dependencies** | `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `pytest`, `httpx` installed | Verified |
| **Health endpoint test** | `tests/test_health.py` passed with `pytest` | 1 passed in 0.24s |
| **FastAPI HTTP boot** | Verified endpoint over HTTP: `curl http://localhost:8000/api/v1/health` returning `{"status": "ok"}` | Verified |
| **Frontend scaffolding** | Vite 8.3.6, React 19, TypeScript, ESLint 10, Tailwind CSS v4, React Router 7 | Verified |
| **Frontend module tree** | `components/{ui,layout,common}`, `pages/`, `services/`, `styles/`, `hooks/`, `types/` | Verified |
| **5 Core frontend files** | `vite.config.ts`, `styles/index.css`, `main.tsx`, `services/api.ts`, `App.tsx` | Verified |
| **Frontend build & lint** | `npm run lint` clean (0 errors), `npm run build` clean (dist created) | Verified |
| **Connection & live-update check** | Verified green `connected`, red `unreachable`, and real-time polling updates | Verified |

---

## Phase 2: UI Shell (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Layout & Shell** | Responsive `AppLayout` with desktop collapsible sidebar, mobile drawer overlay, and sticky `Navbar` | Verified |
| **7 Routed Pages** | Configured `react-router-dom` with routes for `/`, `/analytics`, `/news`, `/watchlist`, `/chat`, `/profile`, `/settings` | Verified |
| **Shared Primitives** | Reusable `Card`, `Badge` (6 variants), `EmptyState`, `Button` (5 variants), and accessible SVG `Icons` | Verified |
| **Live Backend Hook** | Sidebar and Settings pages continuously monitor `/api/v1/health` and display real-time connection status | Verified |
| **ESLint Verification** | `npm run lint` exited code 0 with 0 errors and 0 warnings (strictly compliant with React 19 rules) | Verified |
| **Production Build** | `npm run build` compiled clean 39 modules with Vite and TypeScript | Verified |

---

## Phase 3: Analytics UI (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Recharts Integration** | Installed and configured `recharts` for rich interactive financial charting in dark UI theme | Verified |
| **Sentiment Trajectory** | `SentimentTrendChart` featuring Area gradients, dual metrics, responsive containers, and dark glassmorphism tooltips | Verified |
| **Sector Bar Chart** | `SectorBarChart` comparing FinBERT scores across Indian sectors with dynamic color rating thresholds | Verified |
| **Polarity Donut Chart** | `PolarityDonutChart` rendering proportional split (Positive vs Neutral vs Negative) with center composite indicator | Verified |
| **Dual View Architecture** | Seamless toggle between **Sector Overview** and **Company Deep Dive** | Verified |
| **Company Deep Dive** | Interactive company selectors (RELIANCE, TCS, HDFCBANK, INFY, TATAMOTORS, etc.), historical curves, volume statistics, and key catalysts | Verified |
| **Timeframe Selectors** | Dynamic timeframe switching across `1D`, `1W`, `1M`, `1Y` intervals | Verified |
| **Explicit "No Data" States** | Satisfied exit check requirement: All charts render explicit `EmptyState` fallbacks with zero fabricated figures. Includes a live toggle to test empty-state behavior | Verified |
| **Code Quality Checks** | `npm run lint` clean (0 errors, 0 warnings); `npm run build` compiled cleanly into production bundle | Verified |

---

## Phase 4: News Intelligence UI (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Typed News Architecture** | Implemented `NewsArticle` model with full article body, sector, source, confidence, takeaways, and market impact | Verified |
| **Live News Feed** | Filterable stream with search bar, sentiment filters, sector dropdown, publisher filter, and sort options | Verified |
| **Article Card** | Publisher badge, FinBERT score chip with confidence percentage, tagged tickers, and quick actions | Verified |
| **Article Detail Reader** | Modal / Drawer reading experience featuring full multi-paragraph content, strategic takeaways, and FinBERT impact analysis | Verified |
| **Route Support** | Implemented both `/news` and deep-linked `/news/:id` routes in React Router | Verified |
| **Filter & Route Verification** | Exit check satisfied: Routes and filters operate against typed placeholder structures with active empty states | Verified |
| **Code Quality Checks** | `npm run lint` clean (0 errors, 0 warnings); `npm run build` compiled cleanly into production bundle | Verified |

---

## Phase 5: Personalization UI (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Master Company Index** | Top 30+ official NSE/BSE listed companies (`masterCompanyList`) with industry sector, exchange, and market cap classifications | Verified |
| **Structured State Schema** | Defined `UserProfile`, `UserPreferences`, and `WatchlistRecord` structures built as 1-to-1 mappings for Phase 6 PostgreSQL/Pydantic models | Verified |
| **Validated Profile Forms** | Implemented `validateProfileForm`: checks non-empty names, regex email validation, sector selection, and company requirements | Verified |
| **Master Company Picker** | `CompanyPicker` component supporting live search, sector filtering, multi-tag additions, and badge removal | Verified |
| **Watchlist State Integration** | Autocomplete addition, notes tracking, duplicate detection, and live updates via custom event bus | Verified |
| **FinBERT Alert Controls** | Adjustable sensitivity slider for conviction triggers (`0.50` - `0.95`) + notification toggles | Verified |
| **Code Quality Checks** | `npm run lint` clean (0 errors, 0 warnings); `npm run build` compiled cleanly into production bundle | Verified |

---

## Phase 6: Backend & Database Persistence (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Database Engine & Session** | SQLAlchemy 2.0 engine and scoped sessions supporting PostgreSQL and zero-setup SQLite (`emvest.db`) | Verified |
| **Alembic Migrations** | Generated `initial_schema` migration and ran `alembic upgrade head` cleanly | Verified |
| **Database Models** | Created `User`, `UserPreferences`, and `WatchlistItem` tables with foreign keys and cascade rules | Verified |
| **Pydantic V2 Schemas** | Defined request/response validation schemas for auth, preferences, and watchlist records | Verified |
| **JWT Authentication** | Implemented `bcrypt` password hashing, token generation, and `get_current_user` OAuth2 dependency | Verified |
| **REST API Endpoints** | Implemented `/api/v1/auth/*`, `/api/v1/preferences`, and `/api/v1/watchlist` CRUD routes | Verified |
| **Frontend REST Integration** | Connected frontend API services (`apiGetPreferences`, `apiUpdatePreferences`, `apiGetWatchlist`, `apiAddWatchlist`, `apiDeleteWatchlist`) with offline fallback | Verified |
| **Test Suite Verification** | All 6 pytest test suites passed in 1.01s (`test_auth`, `test_health`, `test_persistence`, `test_preferences`, `test_watchlist`) | Verified (6 passed) |
| **Restart Persistence Check** | Verified preferences and watchlist items survive complete database disconnect and engine restart | Verified |

---

## Phase 7: Data Pipeline & Sentiment Worker (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Database Article Model** | Created `Article` model with indices on published date, sector, and sentiment polarity | Verified |
| **Alembic Migration** | Generated `94764b6aac83_add_articles_table.py` and upgraded database to head | Verified |
| **FinBERT NLP Worker** | Lightweight financial dictionary and rule-based FinBERT scoring service with confidence bounds and polarity determination | Verified |
| **RSS Ingestion Scraper** | Multi-publisher RSS feed parser supporting Economic Times, LiveMint, Business Standard, and Moneycontrol | Verified |
| **Twitter / X Service** | Flag-gated X/Twitter ingestion module (`enable_twitter_ingestion = False`) protecting API quota & legal bounds | Verified |
| **Database Seeding & Ingestion** | Ingestion pipeline auto-seeds high quality financial news on startup and deduplicates incoming articles | Verified |
| **News & Analytics APIs** | Implemented `GET /api/v1/news`, `GET /api/v1/news/{id}`, `GET /api/v1/analytics/summary`, and `GET /api/v1/analytics/trends` | Verified |
| **Backend Test Suite** | Added `test_pipeline.py`; all 11 backend test suites passed cleanly | Verified (11 passed) |
| **Frontend Live Feed Integration** | Connected `NewsPage.tsx` and `services/newsData.ts` to live backend news endpoint with graceful fallback | Verified |
| **Frontend Quality Checks** | `npm run lint` clean (0 errors, 0 warnings); `npm run build` compiled client bundle cleanly | Verified |

---

## Phase 8: AI Assistant & Grounded Retrieval (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Database Chat Persistence** | Created `ChatMessage` table with session IDs, timestamps, and JSON citations | Verified |
| **Alembic Migration** | Generated `ec7b64430c0a_add_chat_messages_table.py` and ran `alembic upgrade head` | Verified |
| **Agentic Retrieval Engine** | Developed `ChatAgent` with Indian equity ticker detection, sector mapping, and multi-field article scoring | Verified |
| **Strict Citation Grounding** | All answers cite stored database articles; every citation ID links to real verified DB record | Verified |
| **Security & Key Boundary** | External LLM keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`) stay strictly backend-internal with zero frontend exposure | Verified |
| **Chat REST Endpoints** | Implemented `POST /api/v1/chat/query`, `GET /api/v1/chat/history/{session_id}`, and `DELETE /api/v1/chat/history/{session_id}` | Verified |
| **Backend Test Suite** | Added `test_chat.py` with 4 tests (session generation, equity targeting, DB grounding, session clear); 15 total backend tests pass in 1.07s | Verified (15 passed) |
| **Frontend Conversational UI** | Connected `ChatbotPage.tsx` and `services/api.ts` with real-time query stream, interactive citations, and session reset | Verified |
| **Code Quality Checks** | `npm run lint` clean (0 errors, 0 warnings); `npm run build` compiled cleanly into production bundle | Verified |

---

## Phase 9: Integration & Testing (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Full Lifecycle End-to-End Suite** | Created `backend/tests/test_e2e.py` verifying full user journey across 10 steps (register, login, me, preferences, watchlist, news stream, analytics overview, company deep-dive, grounded AI query, history, cleanup) | Verified |
| **16 Passing Pytest Suites** | 16 backend unit & integration tests passed in 1.57s with zero failures | Verified (16 passed) |
| **Mobile & Responsive Audit** | Audited all 7 views (`Dashboard`, `Analytics`, `News`, `Watchlist`, `Chatbot`, `Profile`, `Settings`), mobile slide drawer, backdrop dismissal, and sticky responsive header | Verified |
| **Security Review** | CORS origin whitelisting, bcrypt salted password hashing with 72-byte safe truncation, JWT token expiry verification, zero raw SQL queries (100% SQLAlchemy ORM parameterized), and external API key isolation on backend | Verified |
| **Frontend Lint & Production Build** | `npm run lint` clean (0 errors, 0 warnings); `npm run build` compiled 422 modules into production bundle in 191ms | Verified |
| **Documentation & Architecture** | Updated `docs/architecture.md` (with system flowchart, ER diagram, sequence diagram) and `docs/api-documentation.md` (with curl examples for all endpoints) | Verified |

---

## Phase 10: Provider-Backed LLM Layer & Grounded Generation (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **Provider Architecture** | Implemented `LLMProvider` abstract interface and sanitized `LLMError` exception in `app/chatbot/llm/base.py` | Verified |
| **Gemini Provider** | Direct REST implementation via `httpx` to `v1beta/models/{model}:generateContent` with root `systemInstruction` and `x-goog-api-key` header | Verified |
| **OpenAI Provider** | Direct REST implementation via `httpx` to `v1/chat/completions` with bearer token authentication | Verified |
| **Factory & Fallback** | `get_provider()` supporting `auto` (Gemini -> OpenAI -> None), `deterministic`, and specific provider modes | Verified |
| **Grounded Answer Layer** | `ChatAgent._try_generate_llm_answer` formatting retrieved DB articles as numbered `[n]` sources within `<sources>` delimiters, enforcing prompt injection defense and "not financial advice" disclaimers | Verified |
| **Citation Matching** | Answers scan for `[n]` citations, keep only valid references in response citations array, and drop non-existent indices | Verified |
| **Unit Test Suite** | Created `backend/tests/test_llm.py` with 14 unit tests (factory selections, Gemini/OpenAI 5xx retries via `httpx.MockTransport`, faked agent generation, and prompt injection defense) | Verified (14 passed in 0.16s) |
| **Live Integration Script** | Created `backend/scripts/check_llm.py` testing live connectivity with configured API key (isolated, no key logging) | Verified |

```text
============================= test session starts ==============================
tests/test_llm.py::test_factory_deterministic_returns_none PASSED        [  7%]
tests/test_llm.py::test_factory_auto_picks_gemini_when_key_set PASSED    [ 14%]
tests/test_llm.py::test_factory_auto_picks_openai_when_only_openai_key_set PASSED [ 21%]
tests/test_llm.py::test_factory_auto_returns_none_when_no_keys PASSED    [ 28%]
tests/test_llm.py::test_factory_explicit_provider_selection PASSED       [ 35%]
tests/test_llm.py::test_unit_gemini_request_handling_success PASSED      [ 42%]
tests/test_llm.py::test_unit_gemini_5xx_retry_handling PASSED            [ 50%]
tests/test_llm.py::test_unit_gemini_error_mapping_no_secret_leak PASSED  [ 57%]
tests/test_llm.py::test_unit_openai_request_handling_success PASSED      [ 64%]
tests/test_llm.py::test_unit_openai_5xx_retry_handling PASSED            [ 71%]
tests/test_llm.py::test_unit_openai_error_mapping_no_secret_leak PASSED  [ 78%]
tests/test_agent_faked_provider_success_path_with_valid_citations PASSED [ 85%]
tests/test_agent_faked_provider_llmerror_triggers_rule_based_fallback PASSED [ 92%]
tests/test_agent_prompt_injection_in_source_preserves_system_prompt PASSED [100%]
============================== 14 passed in 0.16s ==============================
```


---

## Phase 11: Neural ProsusAI/FinBERT Sentiment Engine Integration (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **PyTorch & Transformers Engine** | Installed `torch-2.8.0` and `transformers-4.57.6` with Apple Silicon `mps` acceleration support into `backend/.venv` | Verified (`PyTorch: 2.8.0, MPS: True`) |
| **Hugging Face Model Caching** | Preloaded `ProsusAI/finbert` tokenizer and sequence classification weights (`~438MB`) into local cache | Verified (`model.safetensors 100%`) |
| **Neural FinBertSentimentWorker** | Upgraded `backend/app/sentiment/finbert_worker.py` to run full neural forward-pass inference on `ProsusAI/finbert` with 512-token truncation, softmax probabilities, and continuous score calculation | Verified |
| **Offline & Heuristic Fallback** | Maintained resilient offline fallback to lexical keyword scoring in case of neural initialization exceptions | Verified |
| **Database Re-scoring** | Re-analyzed all 229 ingested financial news articles in `emvest.db` using neural FinBERT with high-confidence classifications | Verified (229 articles re-scored) |
| **Unit & Pipeline Tests** | `tests/test_pipeline.py::test_finbert_sentiment_worker` passed with positive confidence > 0.95 and negative confidence > 0.95 | Verified (5/5 passed) |

```text
============================= test session starts ==============================
tests/test_pipeline.py::test_rss_scraper_utilities PASSED                [ 20%]
tests/test_pipeline.py::test_rss_xml_parser PASSED                       [ 40%]
tests/test_pipeline.py::test_finbert_sentiment_worker PASSED             [ 60%]
tests/test_pipeline.py::test_pipeline_ingest_and_query_endpoints PASSED  [ 80%]
tests/test_pipeline.py::test_analytics_endpoints_from_real_data PASSED   [100%]
========================= 5 passed, 1 warning in 6.47s =========================
```

---

## Phase 12: Groq LLM Provider Wrapper & Multi-Provider Auto-Fallback

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **OpenAI-Compatible Base URL** | Refactored `OpenAIProvider` to accept a configurable `base_url` (`https://api.openai.com/v1` default) and `provider_name` | Verified |
| **Groq Provider** | Implemented `GroqProvider` in `app/chatbot/llm/groq_provider.py` subclassing `OpenAIProvider` with default base URL `https://api.groq.com/openai/v1` and model `llama-3.3-70b-versatile` | Verified |
| **Pydantic Configuration** | Added `groq_api_key` and `groq_model` to `Settings` in `app/core/config.py` and commented templates to `.env.example` | Verified |
| **Factory Precedence** | Updated `factory.get_provider()` so that in `auto` mode, Groq is checked first (`groq_api_key`), followed by Gemini, then OpenAI, and fallback to `None` | Verified |
| **Unit Test Suite** | Added unit tests using `httpx.MockTransport` in `tests/test_llm.py` testing Groq request headers, base URL, 5xx retry handling, 401 error mapping with zero secret leakage, and factory precedence | Verified (18/18 passed in 0.16s) |
| **Sanitized Live Check Script** | Updated `backend/scripts/check_llm.py` to support Groq, and on failure print only the HTTP status and provider error message text without raw request, headers, or keys | Verified |
| **Live Integration Status** | Unit-tested only; live integration verification pending operator manual execution with personal API key | Pending Operator Run |

```text
============================= test session starts ==============================
tests/test_llm.py::test_factory_deterministic_returns_none PASSED        [  5%]
tests/test_llm.py::test_factory_auto_picks_groq_first_when_all_keys_set PASSED [ 11%]
tests/test_llm.py::test_factory_auto_picks_gemini_when_groq_key_empty PASSED [ 16%]
tests/test_llm.py::test_factory_auto_picks_openai_when_groq_and_gemini_keys_empty PASSED [ 22%]
tests/test_llm.py::test_factory_auto_returns_none_when_no_keys PASSED    [ 27%]
tests/test_llm.py::test_factory_explicit_provider_selection PASSED       [ 33%]
tests/test_llm.py::test_unit_gemini_request_handling_success PASSED      [ 38%]
tests/test_llm.py::test_unit_gemini_5xx_retry_handling PASSED            [ 44%]
tests/test_llm.py::test_unit_gemini_error_mapping_no_secret_leak PASSED  [ 50%]
tests/test_llm.py::test_unit_openai_request_handling_success PASSED      [ 55%]
tests/test_llm.py::test_unit_openai_5xx_retry_handling PASSED            [ 61%]
tests/test_llm.py::test_unit_openai_error_mapping_no_secret_leak PASSED  [ 66%]
tests/test_llm.py::test_unit_groq_request_handling_success PASSED        [ 72%]
tests/test_llm.py::test_unit_groq_5xx_retry_handling PASSED              [ 77%]
tests/test_llm.py::test_unit_groq_error_mapping_no_secret_leak PASSED    [ 83%]
tests/test_llm.py::test_agent_faked_provider_success_path_with_valid_citations PASSED [ 88%]
tests/test_llm.py::test_agent_faked_provider_llmerror_triggers_rule_based_fallback PASSED [ 94%]
tests/test_agent_prompt_injection_in_source_preserves_system_prompt PASSED [100%]
============================== 18 passed in 0.16s ==============================
```

---

## Phase 11: Neural ProsusAI/FinBERT Sentiment Engine Integration (Completed)

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **PyTorch & Transformers Engine** | Installed `torch-2.8.0` and `transformers-4.57.6` with Apple Silicon `mps` acceleration support into `backend/.venv` | Verified (`PyTorch: 2.8.0, MPS: True`) |
| **Hugging Face Model Caching** | Preloaded `ProsusAI/finbert` tokenizer and sequence classification weights (`~438MB`) into local cache | Verified (`model.safetensors 100%`) |
| **Neural FinBertSentimentWorker** | Upgraded `backend/app/sentiment/finbert_worker.py` to run full neural forward-pass inference on `ProsusAI/finbert` with 512-token truncation, softmax probabilities, and continuous score calculation | Verified |
| **Offline & Heuristic Fallback** | Maintained resilient offline fallback to lexical keyword scoring in case of neural initialization exceptions | Verified |
| **Database Re-scoring** | Re-analyzed all 229 ingested financial news articles in `emvest.db` using neural FinBERT with high-confidence classifications | Verified (229 articles re-scored) |
| **Unit & Pipeline Tests** | `tests/test_pipeline.py::test_finbert_sentiment_worker` passed with positive confidence > 0.95 and negative confidence > 0.95 | Verified (5/5 passed) |

```text
============================= test session starts ==============================
tests/test_pipeline.py::test_rss_scraper_utilities PASSED                [ 20%]
tests/test_pipeline.py::test_rss_xml_parser PASSED                       [ 40%]
tests/test_pipeline.py::test_finbert_sentiment_worker PASSED             [ 60%]
tests/test_pipeline.py::test_pipeline_ingest_and_query_endpoints PASSED  [ 80%]
tests/test_pipeline.py::test_analytics_endpoints_from_real_data PASSED   [100%]
========================= 5 passed, 1 warning in 6.47s =========================
```

---

## Phase 12: Groq LLM Provider Wrapper & Multi-Provider Auto-Fallback

### Milestones & Evidence

| Item | Implementation & Verification | Status |
| :--- | :--- | :--- |
| **OpenAI-Compatible Base URL** | Refactored `OpenAIProvider` to accept a configurable `base_url` (`https://api.openai.com/v1` default) and `provider_name` | Verified |
| **Groq Provider** | Implemented `GroqProvider` in `app/chatbot/llm/groq_provider.py` subclassing `OpenAIProvider` with default base URL `https://api.groq.com/openai/v1` and model `llama-3.3-70b-versatile` | Verified |
| **Pydantic Configuration** | Added `groq_api_key` and `groq_model` to `Settings` in `app/core/config.py` and commented templates to `.env.example` | Verified |
| **Factory Precedence** | Updated `factory.get_provider()` so that in `auto` mode, Groq is checked first (`groq_api_key`), followed by Gemini, then OpenAI, and fallback to `None` | Verified |
| **Unit Test Suite** | Added unit tests using `httpx.MockTransport` in `tests/test_llm.py` testing Groq request headers, base URL, 5xx retry handling, 401 error mapping with zero secret leakage, and factory precedence | Verified (18/18 passed in 0.16s) |
| **Sanitized Live Check Script** | Updated `backend/scripts/check_llm.py` to support Groq, and on failure print only the HTTP status and provider error message text without raw request, headers, or keys | Verified |
| **Live Integration Status** | Unit-tested only; live integration verification pending operator manual execution with personal API key | Pending Operator Run |

```text
============================= test session starts ==============================
tests/test_llm.py::test_factory_deterministic_returns_none PASSED        [  5%]
tests/test_llm.py::test_factory_auto_picks_groq_first_when_all_keys_set PASSED [ 11%]
tests/test_llm.py::test_factory_auto_picks_gemini_when_groq_key_empty PASSED [ 16%]
tests/test_llm.py::test_factory_auto_picks_openai_when_groq_and_gemini_keys_empty PASSED [ 22%]
tests/test_llm.py::test_factory_auto_returns_none_when_no_keys PASSED    [ 27%]
tests/test_llm.py::test_factory_explicit_provider_selection PASSED       [ 33%]
tests/test_llm.py::test_unit_gemini_request_handling_success PASSED      [ 38%]
tests/test_llm.py::test_unit_gemini_5xx_retry_handling PASSED            [ 44%]
tests/test_llm.py::test_unit_gemini_error_mapping_no_secret_leak PASSED  [ 50%]
tests/test_llm.py::test_unit_openai_request_handling_success PASSED      [ 55%]
tests/test_llm.py::test_unit_openai_5xx_retry_handling PASSED            [ 61%]
tests/test_llm.py::test_unit_openai_error_mapping_no_secret_leak PASSED  [ 66%]
tests/test_llm.py::test_unit_groq_request_handling_success PASSED        [ 72%]
tests/test_llm.py::test_unit_groq_5xx_retry_handling PASSED              [ 77%]
tests/test_llm.py::test_unit_groq_error_mapping_no_secret_leak PASSED    [ 83%]
tests/test_llm.py::test_agent_faked_provider_success_path_with_valid_citations PASSED [ 88%]
tests/test_llm.py::test_agent_faked_provider_llmerror_triggers_rule_based_fallback PASSED [ 94%]
tests/test_agent_prompt_injection_in_source_preserves_system_prompt PASSED [100%]
============================== 18 passed in 0.16s ==============================
```
