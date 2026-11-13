from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.api.auth import get_current_user
from app.core.security import get_optional_current_user
from app.chatbot.agent import ChatAgent
from app.schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatHistoryResponse,
    ChatMessageRecord,
    CitationItem,
    ChatSessionSummary,
    ChatSessionCreate,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=List[ChatSessionSummary])
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> List[ChatSessionSummary]:
    """List all saved chat threads with preview and message counts (scoped to current user)."""
    query = db.query(ChatSession)
    if current_user:
        query = query.filter(ChatSession.user_id == current_user.id)
    else:
        query = query.filter(ChatSession.user_id.is_(None))
    sessions = query.order_by(ChatSession.updated_at.desc()).all()

    result: List[ChatSessionSummary] = []
    for s in sessions:
        count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        last_msg = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == s.id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        preview = None
        if last_msg:
            text = last_msg.content.replace("#", "").strip()
            preview = text[:80] + "..." if len(text) > 80 else text

        result.append(
            ChatSessionSummary(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count,
                last_message_preview=preview,
            )
        )
    return result


@router.post("/sessions", response_model=ChatSessionSummary, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    body: Optional[ChatSessionCreate] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> ChatSessionSummary:
    """Create a new chat conversation session."""
    session_id = f"sess-{uuid.uuid4().hex[:12]}"
    title = body.title if (body and body.title) else "New Conversation"
    user_id = current_user.id if current_user else None

    sess = ChatSession(
        id=session_id,
        title=title,
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)

    return ChatSessionSummary(
        id=sess.id,
        title=sess.title,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        message_count=0,
        last_message_preview=None,
    )


@router.post("/query", response_model=ChatQueryResponse)
def query_chat(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> ChatQueryResponse:
    """Submit a query to the AI Assistant with multi-turn memory and source citations."""
    user_id = current_user.id if current_user else None
    return ChatAgent.process_query(db=db, request=request, user_id=user_id)


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> ChatHistoryResponse:
    """Retrieve full conversation history and verifiable citations for a chat session."""
    sess = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if sess and sess.user_id is not None:
        if not current_user or current_user.id != sess.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation thread.",
            )

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
@router.delete("/sessions/{session_id}")
def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> dict:
    """Delete a conversation thread and its messages."""
    sess = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if sess and sess.user_id is not None:
        if not current_user or current_user.id != sess.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )

    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.query(ChatSession).filter(ChatSession.id == session_id).delete()
    db.commit()
    return {"status": "cleared", "session_id": session_id}
