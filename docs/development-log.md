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

### Key Decisions & Adjustments

1. **Environment Manager:** Switched from ad-hoc `.venv` to Python 3.11 Conda environment named `emvest`.
2. **Tailwind CSS v4:** Integrated `@tailwindcss/vite` plugin with `@import "tailwindcss";` in `src/styles/index.css`.
3. **React 19 & ESLint 10 Compatibility:** Adjusted effect subscription pattern in `App.tsx` to satisfy React 19 `react-hooks/set-state-in-effect` linting rules.

### Issues to Track for Future Phases

- **HTTPX / Starlette deprecation note in pytest:** Starlette prefers httpx2 in future versions. Harmless today; revisit during Phase 6 when expanding test suites.
- **npm audit:** Track dependency audit findings before production build; avoid using `--force`.
- **Requirements pinning:** Pin explicit versions in `backend/requirements.txt` before Phase 6.

---

## Next Phase: Phase 2 (UI Shell)

- Implement responsive layout with collapsible sidebar and sticky navbar.
- Configure React Router with 7 core routed pages (Dashboard, Watchlist, News, Analytics, AI Chat, Profile, Settings).
- Build shared reusable UI primitives: `Card`, `Badge`, `EmptyState`, `Button`.
