from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD service for SQLAlchemy models."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """Get a record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: UUID) -> ModelType:
        """Delete a record by ID."""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        db.delete(obj)
        db.commit()
        return obj
    
    def get_by_field(self, db: Session, field_name: str, field_value: Any) -> Optional[ModelType]:
        """Get a record by a specific field value."""
        return db.query(self.model).filter(getattr(self.model, field_name) == field_value).first()
    
    def get_multi_by_field(
        self, db: Session, field_name: str, field_value: Any, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records by a specific field value with pagination."""
        return db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).offset(skip).limit(limit).all()