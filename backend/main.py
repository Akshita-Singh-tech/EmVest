from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine, SessionLocal
from app.api import health, auth, preferences, watchlist, news, analytics
from app.services.ingestion import run_ingestion_pipeline

# Initialize database schema tables on startup
Base.metadata.create_all(bind=engine)

# Ensure baseline real news and sentiment articles are ingested
try:
    with SessionLocal() as db_session:
        run_ingestion_pipeline(db_session, force_seed=False)
except Exception:
    pass

app = FastAPI(
    title=settings.app_name,
    description="Emvest Financial Intelligence & Agentic Stock Market API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs_url": "/docs",
        "status": "online",
    }
