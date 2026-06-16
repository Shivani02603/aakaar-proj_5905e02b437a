from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend.routers.auth import get_current_user
from database.config import SessionLocal
from database.models import User

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic schemas
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[UserResponse])
async def list_users(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [
            UserResponse(
                id=str(user.id),
                email=user.email,
                created_at=user.created_at,
            )
            for user in users
        ]
    finally:
        db.close()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse(
            id=str(user.id),
            email=user.email,
            created_at=user.created_at,
        )
    finally:
        db.close()


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    # Only allow users to update their own profile
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if email is being changed and if it's already taken
        if user_data.email is not None and user_data.email != user.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use",
                )
            user.email = user_data.email

        # Update password if provided
        if user_data.password is not None:
            from backend.routers.auth import get_password_hash
            user.password_hash = get_password_hash(user_data.password)

        db.commit()
        db.refresh(user)

        return UserResponse(
            id=str(user.id),
            email=user.email,
            created_at=user.created_at,
        )
    finally:
        db.close()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    # Only allow users to delete their own account
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        db.delete(user)
        db.commit()
    finally:
        db.close()