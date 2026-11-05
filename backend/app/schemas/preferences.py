import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PreferencesBase(BaseModel):
    experience_level: str = "Intermediate"
    risk_tolerance: str = "Moderate"
    investment_horizon: str = "Medium-Term"
    tracked_sectors: List[str] = Field(default_factory=lambda: [
        "Banking & Financial Services",
        "Information Technology",
        "Automobile & Auto Ancillary"
    ])
    tracked_symbols: List[str] = Field(default_factory=lambda: [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS"
    ])
    sentiment_alert_threshold: float = 0.75
    email_alerts: bool = True
    daily_digest: bool = True
    digest_time: str = "08:30"
    enable_ai_suggestions: bool = True


class PreferencesUpdate(PreferencesBase):
    pass


class PreferencesResponse(PreferencesBase):
    id: int
    user_id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
