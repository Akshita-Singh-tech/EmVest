from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.article import Article
from app.schemas.analytics import (
    SentimentOverviewResponse,
    PolaritySplit,
    SectorAnalyticsResponse,
    SectorSentimentMetric,
    CompanyAnalyticsResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=SentimentOverviewResponse)
def get_sentiment_overview(db: Session = Depends(get_db)):
    articles = db.query(Article).all()
    total = len(articles)

    if total == 0:
        return SentimentOverviewResponse(
            composite_score=0.50,
            overall_sentiment="Neutral",
            total_articles=0,
            polarity=PolaritySplit(
                positive=0, neutral=0, negative=0,
                positive_percentage=0.0, neutral_percentage=0.0, negative_percentage=0.0
            ),
            trajectory=[],
        )

    pos_count = sum(1 for a in articles if a.sentiment == "Positive")
    neu_count = sum(1 for a in articles if a.sentiment == "Neutral")
    neg_count = sum(1 for a in articles if a.sentiment == "Negative")

    avg_score = sum(a.sentiment_score for a in articles) / total
    overall_sentiment = "Bullish" if avg_score > 0.3 else ("Bearish" if avg_score < -0.2 else "Neutral")

    # Aggregate trajectory by date/time
    sorted_articles = sorted(articles, key=lambda a: a.published_at)
    trajectory = []
    for art in sorted_articles:
        trajectory.append({
            "date": art.published_at.strftime("%H:%M") if art.published_at else "09:00",
            "score": round(art.sentiment_score, 2),
            "source": art.source,
            "title": art.title,
        })

    return SentimentOverviewResponse(
        composite_score=round(avg_score, 2),
        overall_sentiment=overall_sentiment,
        total_articles=total,
        polarity=PolaritySplit(
            positive=pos_count,
            neutral=neu_count,
            negative=neg_count,
            positive_percentage=round((pos_count / total) * 100, 1),
            neutral_percentage=round((neu_count / total) * 100, 1),
            negative_percentage=round((neg_count / total) * 100, 1),
        ),
        trajectory=trajectory[-10:],
    )


@router.get("/sectors", response_model=SectorAnalyticsResponse)
def get_sector_analytics(db: Session = Depends(get_db)):
    articles = db.query(Article).all()

    sector_groups: Dict[str, List[float]] = {}
    for a in articles:
        sector_groups.setdefault(a.sector, []).append(a.sentiment_score)

    metrics = []
    for sector, scores in sector_groups.items():
        avg = sum(scores) / len(scores)
        status = "Bullish" if avg >= 0.55 else ("Cautious" if avg <= 0.0 else "Neutral")
        metrics.append(
            SectorSentimentMetric(
                sector=sector,
                score=round(avg, 2),
                article_count=len(scores),
                status=status,
                momentum=f"+{round(avg * 5, 1)}%" if avg >= 0 else f"{round(avg * 5, 1)}%",
            )
        )

    # Sort by score descending
    metrics.sort(key=lambda m: m.score, reverse=True)
    return SectorAnalyticsResponse(sectors=metrics)


@router.get("/company/{symbol}", response_model=CompanyAnalyticsResponse)
def get_company_analytics(symbol: str, db: Session = Depends(get_db)):
    upper_sym = symbol.upper().strip()
    articles = db.query(Article).all()

    # Filter articles matching this symbol
    matched = [a for a in articles if upper_sym in (a.symbols or [])]
    if not matched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sentiment articles found for ticker symbol {upper_sym}.",
        )

    avg_score = sum(a.sentiment_score for a in matched) / len(matched)
    status_label = "Bullish" if avg_score >= 0.4 else ("Bearish" if avg_score <= -0.2 else "Neutral")

    catalysts = []
    recent_list = []
    for a in matched:
        if a.market_impact:
            catalysts.append(a.market_impact)
        recent_list.append({
            "title": a.title,
            "source": a.source,
            "score": a.sentiment_score,
            "sentiment": a.sentiment,
            "published_at": a.published_at.strftime("%Y-%m-%d %H:%M") if a.published_at else "",
        })

    return CompanyAnalyticsResponse(
        symbol=upper_sym,
        score=round(avg_score, 2),
        status=status_label,
        article_count=len(matched),
        catalysts=catalysts[:3],
        recent_articles=recent_list,
    )



from app.services.market_quotes import get_realtime_market_data


@router.get("/quotes")
def get_market_quotes():
    """Returns verified real-time Indian market indices (Nifty, Sensex, Bank Nifty, VIX) and equity quotes."""
    return get_realtime_market_data()
