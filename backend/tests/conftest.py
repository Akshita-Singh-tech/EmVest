import pytest
from app.database.session import SessionLocal
from app.models.chat import ChatSession, ChatMessage


@pytest.fixture(autouse=True)
def clean_test_sessions():
    """Ensure any chat sessions created during a test are cleaned up after the test completes."""
    with SessionLocal() as db:
        before_ids = {s[0] for s in db.query(ChatSession.id).all()}

    yield

    with SessionLocal() as db:
        current_sessions = db.query(ChatSession).all()
        for s in current_sessions:
            if s.id not in before_ids:
                db.query(ChatMessage).filter(ChatMessage.session_id == s.id).delete()
                db.delete(s)
        db.commit()
