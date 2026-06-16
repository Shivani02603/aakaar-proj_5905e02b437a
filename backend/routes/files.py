import os
import shutil
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_db
from database.models import UploadedFile, Session

router = APIRouter(prefix="/api/files", tags=["Files"])


# Pydantic schemas
class UploadedFileResponse(BaseModel):
    id: UUID
    session_id: UUID
    filename: str
    file_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadedFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    session_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file and associate it with a session"""
    # Check if session exists
    session_result = await db.execute(
        Session.__table__.select().where(Session.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Generate unique filename
    file_id = uuid4()
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        await file.close()
    
    # Create database record
    uploaded_file = UploadedFile(
        id=file_id,
        session_id=session_id,
        filename=file.filename,
        file_path=file_path,
        uploaded_at=datetime.utcnow()
    )
    
    db.add(uploaded_file)
    await db.commit()
    await db.refresh(uploaded_file)
    
    return uploaded_file