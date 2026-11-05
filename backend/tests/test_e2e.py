import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_full_application_e2e_lifecycle():
    """End-to-End Test: Simulates a complete user journey through all Emvest modules.

    1. Register new user
    2. Login and acquire JWT
    3. Verify identity via /me
    4. Save personalized investment preferences
    5. Add companies to Watchlist
    6. Retrieve live news stream with FinBERT sentiment
    7. Query sector and company analytics
    8. Interact with Grounded AI Assistant and verify citations
    9. Retrieve chat conversation history
    10. Delete watchlist item and clear chat session
    """
    unique_suffix = uuid.uuid4().hex[:6]
    test_email = f"investor_{unique_suffix}@emvest.ai"
    test_password = "SecureInvestPassword2026!"

    # 1. Register new user
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": test_email, "full_name": "Rohan Sharma", "password": test_password},
    )
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
    token_response = reg_res.json()
    assert token_response["user"]["email"] == test_email
    assert "id" in token_response["user"]

    # 2. Login and acquire JWT
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": test_password},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_data = login_res.json()
    token = token_data["access_token"]
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Verify identity via /me
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email

    # 4. Save personalized investment preferences
    pref_payload = {
        "experience_level": "Intermediate",
        "risk_tolerance": "Moderate",
        "investment_horizon": "Medium-Term",
        "tracked_sectors": ["Banking & Financial Services", "Automobile & Auto Ancillary"],
        "tracked_symbols": ["HDFCBANK", "TATAMOTORS"],
        "sentiment_alert_threshold": 0.75,
        "email_alerts": True,
        "daily_digest": True,
        "digest_time": "08:30",
        "enable_ai_suggestions": True,
    }
    update_pref_res = client.put("/api/v1/preferences", json=pref_payload, headers=headers)
    assert update_pref_res.status_code == 200
    saved_prefs = update_pref_res.json()
    assert saved_prefs["sentiment_alert_threshold"] == 0.75
    assert "HDFCBANK" in saved_prefs["tracked_symbols"]

    # 5. Add companies to Watchlist
    client.delete("/api/v1/watchlist/TATAMOTORS", headers=headers)
    watch_res = client.post(
        "/api/v1/watchlist",
        json={
            "symbol": "TATAMOTORS",
            "name": "Tata Motors Ltd",
            "sector": "Automobile & Auto Ancillary",
            "notes": "Targeting festive season EV margin expansion",
        },
        headers=headers,
    )
    assert watch_res.status_code == 201
    watch_item = watch_res.json()
    assert watch_item["symbol"] == "TATAMOTORS"
    assert watch_item["notes"] == "Targeting festive season EV margin expansion"

    # Verify watchlist retrieval
    get_watch_res = client.get("/api/v1/watchlist", headers=headers)
    assert get_watch_res.status_code == 200
    items = get_watch_res.json()
    assert any(i["symbol"] == "TATAMOTORS" for i in items)

    # 6. Retrieve live news stream with FinBERT sentiment
    news_res = client.get("/api/v1/news")
    assert news_res.status_code == 200
    articles = news_res.json()
    assert len(articles) > 0
    first_article = articles[0]
    assert "sentiment" in first_article
    assert "sentiment_score" in first_article
    assert first_article["sentiment"] in ["Positive", "Neutral", "Negative"]

    # 7. Query sector and company analytics
    overview_res = client.get("/api/v1/analytics/overview")
    assert overview_res.status_code == 200
    overview_data = overview_res.json()
    assert "composite_score" in overview_data
    assert "total_articles" in overview_data

    sector_res = client.get("/api/v1/analytics/sectors")
    assert sector_res.status_code == 200
    sector_data = sector_res.json()
    assert len(sector_data["sectors"]) > 0

    company_res = client.get("/api/v1/analytics/company/TATAMOTORS")
    assert company_res.status_code == 200
    comp_data = company_res.json()
    assert comp_data["symbol"] == "TATAMOTORS"
    assert "score" in comp_data

    # 8. Interact with Grounded AI Assistant and verify citations
    chat_session_id = f"e2e-session-{unique_suffix}"
    chat_res = client.post(
        "/api/v1/chat/query",
        json={
            "query": "What are the latest developments and sentiment for Tata Motors and Indian EV sales?",
            "session_id": chat_session_id,
        },
        headers=headers,
    )
    assert chat_res.status_code == 200
    chat_answer = chat_res.json()
    assert chat_answer["session_id"] == chat_session_id
    assert len(chat_answer["citations"]) > 0
    assert len(chat_answer["suggested_followups"]) > 0
    assert chat_answer["sentiment_summary"] is not None

    # Verify citation authenticity
    for cite in chat_answer["citations"]:
        assert cite["id"] > 0
        assert cite["title"] != ""
        assert cite["source"] != ""

    # 9. Retrieve chat conversation history
    history_res = client.get(f"/api/v1/chat/history/{chat_session_id}", headers=headers)
    assert history_res.status_code == 200
    messages = history_res.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

    # 10. Delete watchlist item and clear chat session
    del_watch_res = client.delete("/api/v1/watchlist/TATAMOTORS", headers=headers)
    assert del_watch_res.status_code == 204

    clear_chat_res = client.delete(f"/api/v1/chat/history/{chat_session_id}", headers=headers)
    assert clear_chat_res.status_code == 200
