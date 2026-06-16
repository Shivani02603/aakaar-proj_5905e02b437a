from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Session, Message


class SessionService:
    @staticmethod
    async def create_session(
        db: AsyncSession,
        name: str,
        user_id: UUID
    ) -> Session:
        """Create a new session"""
        session = Session(
            name=name,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    
    @staticmethod
    async def get_all_sessions(
        db: AsyncSession
    ) -> List[Session]:
        """Get all sessions"""
        result = await db.execute(
            select(Session).order_by(Session.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_session_by_id(
        db: AsyncSession,
        session_id: UUID
    ) -> Optional[Session]:
        """Get a session by ID"""
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_session_messages(
        db: AsyncSession,
        session_id: UUID
    ) -> List[Message]:
        """Get all messages for a session"""
        # First verify session exists
        session = await SessionService.get_session_by_id(db, session_id)
        if not session:
            return []
        
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_session(
        db: AsyncSession,
        session_id: UUID
    ) -> bool:
        """Delete a session and all its related data"""
        session = await SessionService.get_session_by_id(db, session_id)
        if not session:
            return False
        
        await db.delete(session)
        await db.commit()
        return True