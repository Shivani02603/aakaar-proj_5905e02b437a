import os
import shutil
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import UploadedFile, Session


class FileService:
    UPLOAD_DIR = "uploads"
    
    @staticmethod
    async def upload_file(
        db: AsyncSession,
        session_id: UUID,
        upload_file: UploadFile
    ) -> UploadedFile:
        """Upload a file and associate it with a session"""
        # Check if session exists
        session_result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Ensure upload directory exists
        os.makedirs(FileService.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        file_id = uuid4()
        file_extension = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(FileService.UPLOAD_DIR, unique_filename)
        
        # Save file to disk
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        finally:
            await upload_file.close()
        
        # Create database record
        uploaded_file = UploadedFile(
            id=file_id,
            session_id=session_id,
            filename=upload_file.filename,
            file_path=file_path,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(uploaded_file)
        await db.commit()
        await db.refresh(uploaded_file)
        
        return uploaded_file
    
    @staticmethod
    async def get_file_by_id(
        db: AsyncSession,
        file_id: UUID
    ) -> Optional[UploadedFile]:
        """Get an uploaded file by ID"""
        result = await db.execute(
            select(UploadedFile).where(UploadedFile.id == file_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_session_files(
        db: AsyncSession,
        session_id: UUID
    ) -> List[UploadedFile]:
        """Get all files for a session"""
        # Verify session exists
        session_result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        if not session:
            return []
        
        result = await db.execute(
            select(UploadedFile)
            .where(UploadedFile.session_id == session_id)
            .order_by(UploadedFile.uploaded_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_file(
        db: AsyncSession,
        file_id: UUID
    ) -> bool:
        """Delete a file from disk and database"""
        file = await FileService.get_file_by_id(db, file_id)
        if not file:
            return False
        
        # Delete from disk
        try:
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
        except Exception:
            pass  # Continue with database deletion even if file doesn't exist
        
        # Delete from database
        await db.delete(file)
        await db.commit()
        return True