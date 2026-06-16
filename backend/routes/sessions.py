from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_db
from database.models import Session, Message

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


# Pydantic schemas
class SessionBase(BaseModel):
    name: str


class SessionCreate(SessionBase):
    user_id: UUID


class SessionResponse(SessionBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new session"""
    new_session = Session(
        name=session_data.name,
        user_id=session_data.user_id,
        created_at=datetime.utcnow()
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db)
):
    """List all sessions"""
    result = await db.execute(
        Session.__table__.select().order_by(Session.created_at.desc())
    )
    sessions = result.scalars().all()
    return sessions


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a specific session"""
    # First check if session exists
    session_result = await db.execute(
        Session.__table__.select().where(Session.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get messages for this session
    result = await db.execute(
        Message.__table__.select()
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return messages