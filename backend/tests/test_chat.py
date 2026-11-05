import uuid
from fastapi.testclient import TestClient
from main import app
from app.database.session import SessionLocal
from app.models.article import Article

client = TestClient(app)


def test_chat_query_new_session():
    """Verify that a query without session_id generates a session and returns citations."""
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "What is the sentiment and outlook on Indian banking stocks?"},
    )
    assert response.status_code == 200
    data = response.json()

    assert "session_id" in data
    assert data["session_id"] is not None
    assert data["role"] == "assistant"
    assert len(data["answer"]) > 20
    assert "citations" in data
    assert isinstance(data["citations"], list)
    assert len(data["citations"]) > 0
    assert "suggested_followups" in data
    assert len(data["suggested_followups"]) > 0


def test_chat_query_specific_equity():
    """Verify that querying for a specific stock (e.g. Reliance or Tata Motors) targets relevant news."""
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "What is the latest news regarding Tata Motors electric vehicle sales?"},
    )
    assert response.status_code == 200
    data = response.json()

    assert any(
        "tata" in c["title"].lower() or "auto" in (c.get("sector") or "").lower()
        for c in data["citations"]
    )


def test_citations_grounded_in_database():
    """Exit check: Answers cite stored articles, and citation IDs match real database records."""
    response = client.post(
        "/api/v1/chat/query",
        json={"query": "Summarize RBI monetary policy and repo rate implications."},
    )
    assert response.status_code == 200
    data = response.json()

    citations = data["citations"]
    assert len(citations) > 0

    with SessionLocal() as db:
        for cite in citations:
            article_id = cite["id"]
            db_art = db.query(Article).filter(Article.id == article_id).first()
            assert db_art is not None, f"Citation ID {article_id} not found in database!"
            assert db_art.title == cite["title"]
            assert db_art.source == cite["source"]
            assert db_art.sentiment == cite["sentiment"]


def test_chat_history_persistence_and_clear():
    """Verify conversation turns persist across calls and can be retrieved or cleared."""
    test_session = f"test-sess-{uuid.uuid4().hex[:8]}"

    # Turn 1
    r1 = client.post(
        "/api/v1/chat/query",
        json={"query": "Tell me about IT sector guidance.", "session_id": test_session},
    )
    assert r1.status_code == 200
    assert r1.json()["session_id"] == test_session

    # Fetch history
    h_res = client.get(f"/api/v1/chat/history/{test_session}")
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert h_data["session_id"] == test_session
    assert len(h_data["messages"]) == 2
    assert h_data["messages"][0]["role"] == "user"
    assert h_data["messages"][0]["content"] == "Tell me about IT sector guidance."
    assert h_data["messages"][1]["role"] == "assistant"
    assert h_data["messages"][1]["citations"] is not None

    # Clear history
    del_res = client.delete(f"/api/v1/chat/history/{test_session}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "cleared"

    # Confirm cleared
    h_empty = client.get(f"/api/v1/chat/history/{test_session}")
    assert h_empty.status_code == 200
    assert len(h_empty.json()["messages"]) == 0
