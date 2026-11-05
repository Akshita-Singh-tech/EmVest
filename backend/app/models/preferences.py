import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True)

    experience_level = Column(String(50), default="Intermediate")
    risk_tolerance = Column(String(50), default="Moderate")
    investment_horizon = Column(String(50), default="Medium-Term")

    # JSON storage for sectors and symbols arrays (compatible with SQLite & PostgreSQL)
    tracked_sectors = Column(JSON, default=list)
    tracked_symbols = Column(JSON, default=list)

    sentiment_alert_threshold = Column(Float, default=0.75)
    email_alerts = Column(Boolean, default=True)
    daily_digest = Column(Boolean, default=True)
    digest_time = Column(String(10), default="08:30")
    enable_ai_suggestions = Column(Boolean, default=True)

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="preferences")

