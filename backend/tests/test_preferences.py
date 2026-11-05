from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_preferences():
    response = client.get("/api/v1/preferences")
    assert response.status_code == 200
    data = response.json()
    assert "experience_level" in data
    assert "tracked_sectors" in data
    assert "tracked_symbols" in data
    assert isinstance(data["tracked_symbols"], list)


def test_update_preferences_persists():
    update_payload = {
        "experience_level": "Advanced",
        "risk_tolerance": "Aggressive",
        "investment_horizon": "Long-Term",
        "tracked_sectors": ["Information Technology", "Automobile & Auto Ancillary"],
        "tracked_symbols": ["INFY", "TATAMOTORS", "RELIANCE"],
        "sentiment_alert_threshold": 0.85,
        "email_alerts": True,
        "daily_digest": False,
        "digest_time": "09:00",
        "enable_ai_suggestions": True,
    }

    put_res = client.put("/api/v1/preferences", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()
    assert updated_data["experience_level"] == "Advanced"
    assert updated_data["risk_tolerance"] == "Aggressive"
    assert updated_data["sentiment_alert_threshold"] == 0.85
    assert updated_data["tracked_symbols"] == ["INFY", "TATAMOTORS", "RELIANCE"]

    # Verify persistence with a subsequent GET
    get_res = client.get("/api/v1/preferences")
    assert get_res.status_code == 200
    persisted = get_res.json()
    assert persisted["experience_level"] == "Advanced"
    assert persisted["risk_tolerance"] == "Aggressive"
    assert persisted["sentiment_alert_threshold"] == 0.85

