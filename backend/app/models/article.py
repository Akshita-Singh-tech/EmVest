import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from app.database.session import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100), nullable=False, index=True)
    url = Column(String(1000), nullable=False)
    published_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    sector = Column(String(100), nullable=False, index=True)

    # JSON array of ticker symbols, e.g. ["RELIANCE", "TCS"]
    symbols = Column(JSON, default=list)

    # FinBERT Sentiment attributes
    sentiment = Column(String(20), nullable=False, index=True)  # Positive, Neutral, Negative
    sentiment_score = Column(Float, nullable=False)            # -1.0 to 1.0
    sentiment_confidence = Column(Float, nullable=False)       # 0.0 to 1.0

    key_takeaways = Column(JSON, default=list)
    market_impact = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

