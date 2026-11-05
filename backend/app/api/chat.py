from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.api.auth import get_current_user
from app.chatbot.agent import ChatAgent
from app.schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatHistoryResponse,
    ChatMessageRecord,
    CitationItem,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatQueryResponse)
def query_chat(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: None),
) -> ChatQueryResponse:
    """Submit a market research or stock query to the AI Assistant.

    Retrieves matching articles from the database, runs FinBERT analysis,
    synthesizes a response with verifiable citations, and persists the conversation.
    """
    user_id = current_user.id if current_user else None
    return ChatAgent.process_query(db=db, request=request, user_id=user_id)


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
) -> ChatHistoryResponse:
    """Retrieve all messages and source citations for an existing chat session."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    record_list = []
    for m in messages:
        cites = None
        if m.citations:
            cites = [CitationItem(**c) if isinstance(c, dict) else c for c in m.citations]

        record_list.append(
            ChatMessageRecord(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                citations=cites,
                created_at=m.created_at,
            )
        )

    return ChatHistoryResponse(session_id=session_id, messages=record_list)


@router.delete("/history/{session_id}")
def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Clear conversation history for a given session."""
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.commit()
    return {"status": "cleared", "session_id": session_id}
