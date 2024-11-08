#!/usr/bin/env python3
"""Defines a basemodel that all the other models inherit from"""
import uuid
from backend.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func


class BaseModel(db.Model):
    """
    Base model class that includes CRUD operations, timestamp columns,
    and a UUID primary key.

    Attributes:
        id (UUID): The unique identifier for the model instance.
        created_at (DateTime): The timestamp when the instance was created.
        updated_at (DateTime): The timestamp when the instance was last updated.
    """

    __abstract__ = True

    id = db.Column(db.String(40),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()),
                   unique=True,
                   nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, **kwargs):
        """Initialize a new model instance."""
        super().__init__(**kwargs)

    @classmethod
    def get_by_id(cls, id):
        """Get a record by UUID."""
        try:
            return cls.query.filter_by(id=id).first()
        except SQLAlchemyError:
            return None  # Handle invalid ID or database error

    def save(self):
        """Save the record to the database."""
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete the record from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """Update specific fields of the record."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def to_dict(self):
        """Convert the record to a dictionary."""
        created_at = self.created_at.isoformat()
        updated_at = self.updated_at.isoformat()

        return {
            "id": self.id,
            "created_at": created_at if self.created_at else None,
            "updated_at": updated_at if self.updated_at else None,
        }
