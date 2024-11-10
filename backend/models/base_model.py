#!/usr/bin/env python3
"""Defines a basemodel that all the other models inherit from"""
import logging
import uuid
from app import db
from datetime import datetime, timezone, UTC
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class BaseModel(db.Model):
    """
    Base model class that includes CRUD operations, timestamp columns,
    and a UUID primary key.
    Attributes:
        id (UUID): The unique identifier for the model instance.
        created_at (DateTime): The timestamp when the instance was created.
        updated_at (DateTime): The timestamp when the instance was updated.
    """
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name."""
        return cls.__name__.lower() + 's'

    id = db.Column(db.String(40),
                  primary_key=True,
                  default=lambda: str(uuid.uuid4()),
                  unique=True,
                  nullable=False,
                  index=True)

    created_at = db.Column(db.DateTime(timezone=True),
                          server_default=func.now(),
                          nullable=False,
                          index=True)

    updated_at = db.Column(db.DateTime(timezone=True),
                          server_default=func.now(),
                          onupdate=func.now(),
                          nullable=False)

    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize a new model instance with validation."""
        if not kwargs.get('id'):
            kwargs['id'] = str(uuid.uuid4())

        # Validate input data
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Invalid field '{key}' for {self.__class__.__name__}")

        super().__init__(**kwargs)

        if not self.created_at:
            self.created_at = datetime.now(UTC)
        if not self.updated_at:
            self.updated_at = datetime.now(UTC)

    @classmethod
    def get_by_id(cls, id: str, include_deleted: bool = False) -> Optional['BaseModel']:
        """Get a record by ID with improved error handling."""
        if not id:
            return None

        try:
            query = cls.query
            if not include_deleted:
                query = query.filter_by(is_deleted=False)
            return query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {cls.__name__} with id {id}: {str(e)}")
            db.session.rollback()
            return None

    def save(self, commit: bool = True) -> bool:
        """Save the record to database with retry mechanism."""
        MAX_RETRIES = 3
        retry_count = 0

        while retry_count < MAX_RETRIES:
            try:
                if not self.id:
                    self.id = str(uuid.uuid4())

                self.updated_at = datetime.now(UTC)
                db.session.add(self)

                if commit:
                    db.session.commit()
                return True

            except SQLAlchemyError as e:
                retry_count += 1
                err = f"Attempt {retry_count} failed to save {self.__class__.__name__}: {str(e)}"
                logger.warning(err)
                db.session.rollback()

                if retry_count == MAX_RETRIES:
                    err = f"Failed to save {self.__class__.__name__} after {MAX_RETRIES} attempts"
                    logger.error(err)
                    raise

        return False

    def soft_delete(self) -> bool:
        """Soft delete the record."""
        try:
            self.is_deleted = True
            self.deleted_at = datetime.now(UTC)
            self.save()
            return True
        except SQLAlchemyError as e:
            err = f"Error soft deleting {self.__class__.__name__} {self.id}: {str(e)}"
            logger.error(err)
            return False

    def hard_delete(self) -> bool:
        """Permanently delete the record from database."""
        try:
            existing = db.session.get(self.__class__, self.id)
            if not existing:
                raise SQLAlchemyError(f"{self.__class__.__name__} {self.id} does not exist")

            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            err = f"Error deleting {self.__class__.__name__} {self.id}: {str(e)}"
            logger.error(err)
            db.session.rollback()
            raise

    def update(self, **kwargs: Dict[str, Any]) -> bool:
        """Update specific fields with validation and optimistic locking."""
        try:
            # Validate fields
            for key in kwargs:
                if not hasattr(self, key):
                    e = f"Invalid field '{key}' for {self.__class__.__name__}"
                    raise AttributeError(e)

            # Update fields
            for key, value in kwargs.items():
                setattr(self, key, value)

            if self not in db.session:
                db.session.add(self)

            self.updated_at = datetime.now(UTC)
            db.session.commit()

            # Refresh the instance to ensure we have the latest data
            db.session.refresh(self)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.__class__.__name__} {self.id}: {str(e)}")
            db.session.rollback()
            return False

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """Convert record to dictionary with sensitive field exclusion."""
        if exclude is None:
            exclude = set()

        data = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[column.name] = value
        return data
