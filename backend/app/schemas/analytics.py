from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class PolaritySplit(BaseModel):
    positive: int
    neutral: int
    negative: int
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float


class SentimentOverviewResponse(BaseModel):
    composite_score: float
    overall_sentiment: str
    total_articles: int
    polarity: PolaritySplit
    trajectory: List[Dict[str, Any]]


class SectorSentimentMetric(BaseModel):
    sector: str
    score: float
    article_count: int
    status: str
    momentum: str


class SectorAnalyticsResponse(BaseModel):
    sectors: List[SectorSentimentMetric]


class CompanyAnalyticsResponse(BaseModel):
    symbol: str
    score: float
    status: str
    article_count: int
    catalysts: List[str]
    recent_articles: List[Dict[str, Any]]
