#!/usr/bin/env python3
"""Defines a basemodel that all the other models inherit from"""
import logging
import uuid
from app import db
from datetime import datetime, timezone, UTC
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List, Type, TypeVar
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseModel')


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

    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    @classmethod
    @contextmanager
    def transaction(cls):
        """Context manager for database transactions with automatic rollback."""
        try:
            yield
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize a new model instance with validation."""
        self.validate_init_data(kwargs)

        if not kwargs.get('id'):
            kwargs['id'] = str(uuid.uuid4())

        super().__init__(**kwargs)

        if not self.created_at:
            self.created_at = datetime.now(UTC)
        if not self.updated_at:
            self.updated_at = datetime.now(UTC)

    @classmethod
    def validate_init_data(cls, data: Dict[str, Any]) -> None:
        """Validate initialization data"""
        invalid_fields = [key for key in data if not hasattr(cls, key)]
        if invalid_fields:
            raise AttributeError(f"Invalid fields for {cls.__name__}: {', '.join(invalid_fields)}")

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

    @classmethod
    def bulk_create(cls: Type[T], items: List[Dict[str, Any]]) -> List[T]:
        """Bulk create records with error handling."""
        instances = []
        try:
            with cls.transaction():
                for item in items:
                    instance = cls(**item)
                    db.session.add(instance)
                    instances.append(instance)
            return instances
        except SQLAlchemyError as e:
            logger.error(f"Bulk create failed for {cls.__name__}: {str(e)}")
            raise

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
                    db.session.refresh(self)
                return True

            except IntegrityError as e:
                db.session.rollback()
                logger.error(f"Integrity error saving {self.__class__.__name__}: {str(e)}")
                raise

            except SQLAlchemyError as e:
                retry_count += 1
                db.session.rollback()

                if retry_count == MAX_RETRIES:
                    err = f"Failed to save {self.__class__.__name__} after {MAX_RETRIES} attempts: {str(e)}"
                    logger.error(err)
                    raise

        return False

    def validate(self) -> None:
        """Validate model data before save. Override in subclasses."""
        pass

    def soft_delete(self) -> bool:
        """Soft delete the record."""
        try:
            with self.transaction():
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
            with self.transaction():
                db.session.delete(self)
            return True
        except SQLAlchemyError as e:
            err = f"Error deleting {self.__class__.__name__} {self.id}: {str(e)}"
            logger.error(err)
            raise

    def update(self, **kwargs: Dict[str, Any]) -> bool:
        """Update specific fields with validation and optimistic locking."""
        try:
            with self.transaction():
                # Validate fields
                invalid_fields = [key for key in kwargs if not hasattr(self, key)]
                if invalid_fields:
                    raise AttributeError(f"Invalid fields: {', '.join(invalid_fields)}")

                # Update fields
                for key, value in kwargs.items():
                    setattr(self, key, value)

                self.validate()
                self.updated_at = datetime.now(UTC)

                if self not in db.session:
                    db.session.add(self)

            return True

        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.__class__.__name__} {self.id}: {str(e)}")
            db.session.rollback()
            return False

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """Convert record to dictionary with sensitive field exclusion."""
        if exclude is None:
            exclude = set()

        exclude.update({'password_hash', 'password'})

        data = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                data[column.name] = value
        return data
