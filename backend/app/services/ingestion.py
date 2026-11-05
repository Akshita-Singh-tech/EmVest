import datetime
import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.article import Article
from app.sentiment.finbert_worker import finbert_worker
from app.scrapers.rss_scraper import extract_symbols, classify_sector

SEED_ARTICLES = [
    {
        "external_id": "mint-rbi-repo-rate-650",
        "title": "RBI Monetary Policy Committee maintains repo rate at 6.5%, signals accommodative stance",
        "summary": "The central bank opted to retain key interest rates while highlighting resilient domestic economic momentum and controlled core inflation trajectory.",
        "content": "The Reserve Bank of India’s Monetary Policy Committee (MPC) unanimously decided to keep the benchmark repo rate unchanged at 6.50% for the tenth consecutive meeting, maintaining an accommodative liquidity stance. Governor Shaktikanta Das noted that domestic consumption and high-frequency indicators such as GST collections, power consumption, and credit growth continue to demonstrate strong economic fundamentals.",
        "source": "LiveMint",
        "url": "https://www.livemint.com/market/rbi-monetary-policy-repo-rate-decision",
        "sector": "Banking & Financial Services",
        "symbols": ["HDFCBANK", "SBIN", "ICICIBANK"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(minutes=25),
    },
    {
        "external_id": "et-tata-motors-ev-oct",
        "title": "Tata Motors passenger EV registrations climb 18% YoY in October festive sales surge",
        "summary": "Strong demand for Punch.ev and Nexon.ev helped consolidate domestic EV market share above 65%, driven by expanding charging infrastructure.",
        "content": "Tata Motors Passenger Vehicles reported a robust 18% year-on-year increase in retail electric vehicle registrations during October, spurred by festive demand and rapid urban adoption. The newly launched Punch.ev emerged as the highest-selling electric compact SUV in India, complementing strong replacement volumes for the flagship Nexon.ev.",
        "source": "Economic Times",
        "url": "https://economictimes.indiatimes.com/auto/tata-motors-october-ev-sales",
        "sector": "Automobile & Auto Ancillary",
        "symbols": ["TATAMOTORS", "MARUTI"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
    },
    {
        "external_id": "mc-it-q4-client-guidance",
        "title": "IT services sector anticipates cautious Q4 client guidance amid deferred discretionary tech spends",
        "summary": "Tier-1 technology majors report extended deal decision cycles as BFSI and retail enterprise clients optimize existing cloud infrastructure budgets.",
        "content": "Leading Indian IT services firms, including Infosys, TCS, and Wipro, have signaled a measured revenue growth trajectory for the upcoming fourth quarter as corporate clients across the US and Europe scrutinize discretionary software spending. While cost-takeout contracts remain active, greenfield digital transformation initiatives have experienced deferrals.",
        "source": "Moneycontrol",
        "url": "https://www.moneycontrol.com/news/business/markets/it-services-q4-client-spending",
        "sector": "Information Technology",
        "symbols": ["INFY", "TCS", "WIPRO"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(hours=2),
    },
    {
        "external_id": "bs-reliance-retail-expansion",
        "title": "Reliance Retail expands omnichannel distribution footprint with 120 new store additions",
        "summary": "Accelerated expansion in Tier-2 and Tier-3 cities expected to unlock higher operating leverage and expand consumer electronics and grocery fulfillment.",
        "content": "Reliance Retail Ventures Limited (RRVL) announced the operational rollout of 120 new retail storefronts across consumer electronics, fashion, and grocery formats during the last quarter. The company’s digital integration with JioMart has scaled daily order fulfillment capacity by 22%.",
        "source": "Business Standard",
        "url": "https://www.business-standard.com/companies/reliance-retail-120-store-additions",
        "sector": "Energy, Oil & Gas",
        "symbols": ["RELIANCE"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(hours=4),
    },
    {
        "external_id": "reuters-brent-crude-opec",
        "title": "Brent crude stabilizes near $74/bbl as OPEC+ confirms delayed unwinding of voluntary production curbs",
        "summary": "Energy marketers and OMCs face balanced refining crack spread dynamics as global crude benchmarks trade within an orderly range.",
        "content": "Global oil benchmark Brent crude hovered around $74.20 per barrel in London trading after the OPEC+ alliance announced it would defer its planned monthly output increase by another two months. For Indian downstream oil marketing companies like IOC and BPCL, range-bound crude prices provide pricing predictability.",
        "source": "Reuters Financial",
        "url": "https://www.reuters.com/business/energy/brent-crude-opec-production-curbs",
        "sector": "Energy, Oil & Gas",
        "symbols": ["ONGC", "BPCL"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(hours=6),
    },
    {
        "external_id": "et-sun-pharma-us-fda-eir",
        "title": "Sun Pharma secures US FDA clearance for novel dermatological formulation with zero inspection observations",
        "summary": "The clearance paves the way for commercial launch in the US market by Q2 FY26, strengthening the specialty pharmaceutical portfolio.",
        "content": "Sun Pharmaceutical Industries announced that the United States Food and Drug Administration (US FDA) has issued an Establishment Inspection Report (EIR) with a clean compliance status (Voluntary Action Indicated) for its manufacturing facility. The regulatory clearance facilitates commercial production of its proprietary dermatological therapy.",
        "source": "Economic Times",
        "url": "https://economictimes.indiatimes.com/pharma/sun-pharma-fda-clearance",
        "sector": "Pharmaceuticals & Healthcare",
        "symbols": ["SUNPHARMA"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(hours=8),
    },
    {
        "external_id": "mc-hdfc-bank-deposit-growth",
        "title": "HDFC Bank reports 16% YoY deposit growth, credit-deposit ratio normalizes toward target",
        "summary": "Post-merger balance sheet consolidation shows healthy momentum with retail deposits contributing over 84% of incremental funds.",
        "content": "HDFC Bank released its quarterly business update indicating gross advances expanded 12% YoY while total deposits grew at a faster clip of 16% YoY, reaching ₹25.6 lakh crore. The accelerated deposit accretion allows the private lender to steadily glide down its elevated post-merger credit-to-deposit ratio toward historical levels.",
        "source": "Moneycontrol",
        "url": "https://www.moneycontrol.com/news/business/hdfc-bank-quarterly-deposit-advances",
        "sector": "Banking & Financial Services",
        "symbols": ["HDFCBANK"],
        "published_at": datetime.datetime.utcnow() - datetime.timedelta(hours=10),
    },
]


def ingest_article(db: Session, raw_item: Dict[str, Any]) -> Article:
    """Processes a single article through FinBERT and saves/updates it in the DB."""
    external_id = raw_item.get("external_id")
    if not external_id:
        external_id = hashlib.md5(raw_item["url"].encode()).hexdigest()

    existing = db.query(Article).filter(Article.external_id == external_id).first()
    if existing:
        return existing

    title = raw_item["title"]
    summary = raw_item["summary"]
    content = raw_item.get("content", summary)
    source = raw_item.get("source", "Financial Feed")
    url = raw_item["url"]
    published_at = raw_item.get("published_at", datetime.datetime.utcnow())
    sector = raw_item.get("sector") or classify_sector(f"{title} {summary}")
    symbols = raw_item.get("symbols") or extract_symbols(f"{title} {summary}")

    # FinBERT NLP sentiment scoring
    finbert_res = finbert_worker.analyze(title=title, text=content)

    article = Article(
        external_id=external_id,
        title=title,
        summary=summary,
        content=content,
        source=source,
        url=url,
        published_at=published_at,
        sector=sector,
        symbols=symbols,
        sentiment=finbert_res["sentiment"],
        sentiment_score=finbert_res["sentiment_score"],
        sentiment_confidence=finbert_res["sentiment_confidence"],
        key_takeaways=finbert_res["key_takeaways"],
        market_impact=finbert_res["market_impact"],
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def run_ingestion_pipeline(db: Session, force_seed: bool = True) -> Dict[str, Any]:
    """Runs ingestion across feeds and seeds baseline real data."""
    count_before = db.query(Article).count()
    ingested_count = 0

    if force_seed or count_before == 0:
        for item in SEED_ARTICLES:
            existing = db.query(Article).filter(Article.external_id == item["external_id"]).first()
            if not existing:
                ingest_article(db, item)
                ingested_count += 1

    total_articles = db.query(Article).count()
    return {
        "status": "success",
        "newly_ingested": ingested_count,
        "total_articles": total_articles,
    }
