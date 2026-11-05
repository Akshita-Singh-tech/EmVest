from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CitationItem(BaseModel):
    id: int
    title: str
    source: str
    url: str
    published_at: Optional[str] = None
    sentiment: str
    sentiment_score: float
    symbols: List[str] = Field(default_factory=list)
    sector: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    symbols: Optional[List[str]] = None


class SentimentSummary(BaseModel):
    aggregate_score: float
    sentiment_label: str
    article_count: int
    positive_count: int
    neutral_count: int
    negative_count: int


class ChatQueryResponse(BaseModel):
    session_id: str
    role: str = "assistant"
    answer: str
    citations: List[CitationItem] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)
    sentiment_summary: Optional[SentimentSummary] = None


class ChatMessageRecord(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    citations: Optional[List[CitationItem]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageRecord]
