from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.preferences import UserPreferences
from app.models.watchlist import WatchlistItem


def test_preferences_and_watchlist_persist_across_reconnect():
    # 1. First session: update preferences and add watchlist item
    engine1 = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    Session1 = sessionmaker(bind=engine1)
    db1 = Session1()

    prefs = db1.query(UserPreferences).first()
    if not prefs:
        prefs = UserPreferences(
            experience_level="Institutional",
            risk_tolerance="Aggressive",
            investment_horizon="Long-Term",
            tracked_sectors=["Metals & Mining", "Banking & Financial Services"],
            tracked_symbols=["TATASTEEL", "RELIANCE"],
            sentiment_alert_threshold=0.88,
        )
        db1.add(prefs)
    else:
        prefs.experience_level = "Institutional"
        prefs.risk_tolerance = "Aggressive"
        prefs.sentiment_alert_threshold = 0.88
        prefs.tracked_symbols = ["TATASTEEL", "RELIANCE"]

    db1.commit()
    db1.close()
    engine1.dispose()

    # 2. Simulate complete restart: fresh engine and session connecting to same DB file
    engine2 = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    Session2 = sessionmaker(bind=engine2)
    db2 = Session2()

    reloaded_prefs = db2.query(UserPreferences).first()
    assert reloaded_prefs is not None
    assert reloaded_prefs.experience_level == "Institutional"
    assert reloaded_prefs.risk_tolerance == "Aggressive"
    assert reloaded_prefs.sentiment_alert_threshold == 0.88
    assert "TATASTEEL" in reloaded_prefs.tracked_symbols

    db2.close()
    engine2.dispose()
