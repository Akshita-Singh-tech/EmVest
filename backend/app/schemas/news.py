import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ArticleResponse(BaseModel):
    id: int
    external_id: str
    title: str
    summary: str
    content: str
    source: str
    url: str
    published_at: datetime.datetime
    sector: str
    symbols: List[str]
    sentiment: str
    sentiment_score: float
    sentiment_confidence: float
    key_takeaways: List[str]
    market_impact: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class IngestionResponse(BaseModel):
    status: str
    newly_ingested: int
    total_articles: int

