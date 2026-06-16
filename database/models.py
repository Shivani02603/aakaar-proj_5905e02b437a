import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4, UUID

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    Index,
    text
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session as DBSession

# Environment variable for database URL
DATABASE_URL_ENV = "DATABASE_URL"

# Get database URL from environment
DATABASE_URL = os.environ.get(DATABASE_URL_ENV)
if not DATABASE_URL:
    raise ValueError(f"Environment variable {DATABASE_URL_ENV} is not set")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, created_at={self.created_at})>"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="session", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, name={self.name}, created_at={self.created_at})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index("ix_messages_session_id", "session_id"),
        Index("ix_messages_created_at", "created_at"),
        Index("ix_messages_role", "role"),
    )

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role}, content='{content_preview}', created_at={self.created_at})>"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="uploaded_files")
    document_chunks = relationship("DocumentChunk", back_populates="uploaded_file", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_uploaded_files_session_id", "session_id"),
        Index("ix_uploaded_files_filename", "filename"),
        Index("ix_uploaded_files_uploaded_at", "uploaded_at"),
    )

    def __repr__(self) -> str:
        return f"<UploadedFile(id={self.id}, session_id={self.session_id}, filename={self.filename}, file_path={self.file_path}, uploaded_at={self.uploaded_at})>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    uploaded_file_id = Column(PG_UUID(as_uuid=True), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column("embedding", type_=Text)  # Will be converted to vector type via pgvector
    row_start = Column(Integer, nullable=False)
    row_end = Column(Integer, nullable=False)

    # Relationships
    uploaded_file = relationship("UploadedFile", back_populates="document_chunks")

    # Indexes
    __table_args__ = (
        Index("ix_document_chunks_uploaded_file_id", "uploaded_file_id"),
        Index("ix_document_chunks_chunk_index", "chunk_index"),
        Index("ix_document_chunks_row_start", "row_start"),
        Index("ix_document_chunks_row_end", "row_end"),
    )

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<DocumentChunk(id={self.id}, uploaded_file_id={self.uploaded_file_id}, chunk_index={self.chunk_index}, content='{content_preview}', row_start={self.row_start}, row_end={self.row_end})>"