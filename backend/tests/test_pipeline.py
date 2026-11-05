from fastapi.testclient import TestClient
from main import app
from app.sentiment.finbert_worker import finbert_worker
from app.scrapers.rss_scraper import clean_html, extract_symbols, classify_sector, parse_rss_xml

client = TestClient(app)


def test_rss_scraper_utilities():
    raw_html = "<p>Reliance Retail reports <b>strong profit</b> surge &amp; expansion.</p>"
    cleaned = clean_html(raw_html)
    assert "<" not in cleaned
    assert "Reliance Retail reports" in cleaned

    symbols = extract_symbols("HDFC Bank and Tata Motors rally on earnings optimism.")
    assert "HDFCBANK" in symbols
    assert "TATAMOTORS" in symbols

    sector = classify_sector("RBI MPC leaves repo rate unchanged at 6.5%.")
    assert sector == "Banking & Financial Services"


def test_rss_xml_parser():
    sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Financial News</title>
            <link>https://example.com</link>
            <item>
                <title>Infosys wins $400M digital transformation contract</title>
                <link>https://example.com/news/1</link>
                <description>Infosys has expanded its multi-year deal pipeline.</description>
                <guid>test-guid-infy-1</guid>
            </item>
        </channel>
    </rss>
    """
    items = parse_rss_xml(sample_rss, "TestPublisher")
    assert len(items) == 1
    assert items[0]["external_id"] == "test-guid-infy-1"
    assert "INFY" in items[0]["symbols"]
    assert items[0]["sector"] == "Information Technology"


def test_finbert_sentiment_worker():
    # Bullish text
    bullish = finbert_worker.analyze(
        title="Tata Motors passenger EV registrations surge 18% with robust margin expansion",
        text="Strong festive demand and Punch.ev deliveries consolidated dominant market share."
    )
    assert bullish["sentiment"] == "Positive"
    assert bullish["sentiment_score"] > 0
    assert bullish["sentiment_confidence"] >= 0.80
    assert len(bullish["key_takeaways"]) > 0

    # Bearish text
    bearish = finbert_worker.analyze(
        title="IT sector guidance cautious as client discretionary tech spends slow down",
        text="Deal review cycles extended and enterprise software budgets face deferrals."
    )
    assert bearish["sentiment"] == "Negative"
    assert bearish["sentiment_score"] < 0
    assert bearish["sentiment_confidence"] >= 0.80


def test_pipeline_ingest_and_query_endpoints():
    # 1. Trigger ingestion endpoint
    ingest_res = client.post("/api/v1/news/ingest")
    assert ingest_res.status_code == 200
    ingest_data = ingest_res.json()
    assert ingest_data["status"] == "success"
    assert ingest_data["total_articles"] >= 5

    # 2. Query news feed
    news_res = client.get("/api/v1/news")
    assert news_res.status_code == 200
    articles = news_res.json()
    assert len(articles) >= 5

    # Check article attributes
    first = articles[0]
    assert "title" in first
    assert "sentiment" in first
    assert "sentiment_score" in first
    assert "symbols" in first
    assert isinstance(first["symbols"], list)
    assert "key_takeaways" in first

    # 3. Filter by sentiment
    pos_res = client.get("/api/v1/news?sentiment=Positive")
    assert pos_res.status_code == 200
    pos_articles = pos_res.json()
    assert all(a["sentiment"] == "Positive" for a in pos_articles)

    # 4. Filter by symbol
    rel_res = client.get("/api/v1/news?symbol=RELIANCE")
    assert rel_res.status_code == 200
    rel_articles = rel_res.json()
    assert any("RELIANCE" in a["symbols"] for a in rel_articles)


def test_analytics_endpoints_from_real_data():
    # 1. Sentiment overview
    overview_res = client.get("/api/v1/analytics/overview")
    assert overview_res.status_code == 200
    overview = overview_res.json()
    assert overview["total_articles"] >= 5
    assert "composite_score" in overview
    assert "polarity" in overview
    assert overview["polarity"]["positive"] + overview["polarity"]["neutral"] + overview["polarity"]["negative"] == overview["total_articles"]

    # 2. Sector analytics
    sectors_res = client.get("/api/v1/analytics/sectors")
    assert sectors_res.status_code == 200
    sectors_data = sectors_res.json()
    assert len(sectors_data["sectors"]) > 0
    first_sector = sectors_data["sectors"][0]
    assert "sector" in first_sector
    assert "score" in first_sector
    assert "article_count" in first_sector

    # 3. Company analytics
    company_res = client.get("/api/v1/analytics/company/HDFCBANK")
    assert company_res.status_code == 200
    company_data = company_res.json()
    assert company_data["symbol"] == "HDFCBANK"
    assert company_data["article_count"] >= 1
    assert "catalysts" in company_data
