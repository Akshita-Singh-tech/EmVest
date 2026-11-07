from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Emvest API"
    environment: str = "development"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Database
    database_url: str = "sqlite:///./emvest.db"

    # Security
    jwt_secret: str = "emvest-dev-super-secret-key-phase6-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Phase 7: Data Pipeline & Optional X/Twitter Flag
    enable_twitter_ingestion: bool = False
    twitter_bearer_token: Optional[str] = None

    # Phase 8: AI Assistant & LLM Service (Keys stay exclusively on backend)
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    default_llm_provider: str = "auto"  # "auto", "gemini", "openai", "deterministic"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()
