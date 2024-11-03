#!/usr/bin/env python3
"""Defines a basemodel that all the other models inherit from"""
from backend.extensions import db
from backend.models.storage import save, delete

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

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def save(self):
        """Save the record to the database."""
        save(self)

    def delete(self):
        """Delete the record from the database."""
        delete(self)

    def to_dict(self):
        """Convert the record to a dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
