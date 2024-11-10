#!/usr/bin/env python3
"""Defines a basemodel that all the other models inherit from"""
import uuid
from app import db
from datetime import datetime, timezone, UTC
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func


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

    id = db.Column(db.String(40),
                   primary_key=True,
                   default=str(uuid.uuid4()),
                   unique=True,
                   nullable=False)
    # Changed the defaults to pythonic style, datetime.utcnow
    # will be deprected
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(),
                           nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(),
                           onupdate=func.now())

    def __init__(self, **kwargs):
        """Initialize a new model instance."""
        if not kwargs.get('id'):
            self.id = str(uuid.uuid4())
        super().__init__(**kwargs)

        if not self.created_at:
            self.created_at = datetime.now(UTC)
        if not self.updated_at:
            self.updated_at = datetime.now(UTC)

    @classmethod
    def get_by_id(cls, id):
        """Get a record by ID."""
        if not id:
            return None
        try:
            instance = db.session.get(cls, id)
            if instance is not None:
                return instance
            return cls.query.filter_by(id=id).first()
        except SQLAlchemyError:
            db.session.rollback()
            return None

    def save(self):
        """Save the record to the database."""
        try:
            if not self.id:
                self.id = str(uuid.uuid4())

            if not self.created_at:
                self.created_at = datetime.now(UTC)
            self.updated_at = datetime.now(UTC)

            existing = db.session.get(self.__class__, self.id)
            if existing is not None and existing is not self:
                db.session.expunge(existing)

            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete the record from the database."""
        try:
            instance = db.session.get(self.__class__, self.id)
            if instance is not None:
                db.session.delete(instance)
                db.session.commit()
                return True
            else:
                raise SQLAlchemyError("Instance not found in database")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """Update specific fields of the record."""
        try:
            instance = db.session.get(self.__class__, self.id)
            if instance is None:
                raise SQLAlchemyError("Instance not found in database")

            for key, value in kwargs.items():
                if not hasattr(self, key):
                    e = f"'{self.__class__.__name__}' has no attribute '{key}'"
                    raise AttributeError(e)
                setattr(instance, key, value)

            instance.updated_at = datetime.now(UTC)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def to_dict(self):
        """Convert the record to a dictionary."""
        created_at = self.created_at.isoformat() if self.created_at else None
        updated_at = self.updated_at.isoformat() if self.updated_at else None

        return {
            "id": self.id,
            "created_at": created_at,
            "updated_at": updated_at,
        }
