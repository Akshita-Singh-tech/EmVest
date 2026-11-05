from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # List of citation objects
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

