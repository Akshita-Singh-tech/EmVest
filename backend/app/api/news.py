from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.database.session import get_db
from app.models.article import Article
from app.schemas.news import ArticleResponse, IngestionResponse
from app.services.ingestion import run_ingestion_pipeline

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=List[ArticleResponse])
def get_articles(
    search: Optional[str] = Query(None, description="Search query across title and summary"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (Positive, Neutral, Negative)"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    source: Optional[str] = Query(None, description="Filter by publisher source"),
    symbol: Optional[str] = Query(None, description="Filter by stock ticker symbol"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Article)

    if sentiment and sentiment.lower() != "all":
        query = query.filter(Article.sentiment == sentiment.capitalize())

    if sector and sector.lower() != "all sectors":
        query = query.filter(Article.sector.ilike(f"%{sector}%"))

    if source and source.lower() != "all publishers":
        query = query.filter(Article.source.ilike(f"%{source}%"))

    if search and search.strip():
        q_pattern = f"%{search.strip()}%"
        query = query.filter(or_(Article.title.ilike(q_pattern), Article.summary.ilike(q_pattern)))

    if symbol and symbol.strip():
        sym_upper = symbol.strip().upper()
        # JSON array contains symbol check or string match
        query = query.filter(Article.symbols.contains(sym_upper))

    articles = query.order_by(desc(Article.published_at)).offset(offset).limit(limit).all()
    return [ArticleResponse.model_validate(a) for a in articles]


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found",
        )
    return ArticleResponse.model_validate(article)


@router.post("/ingest", response_model=IngestionResponse)
def trigger_ingestion(db: Session = Depends(get_db)):
    result = run_ingestion_pipeline(db, force_seed=True)
    return IngestionResponse(**result)
