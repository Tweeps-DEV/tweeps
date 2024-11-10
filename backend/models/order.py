#!usr/bin/env python3
"""Defines an Order model"""
import uuid
from app import db
from datetime import datetime, timezone, UTC
from models.base_model import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from time import sleep


class Order(BaseModel):
    """
    Represents an order in the system.

    This class defines the structure of Order objects
    and their relationship to Users.

    Attributes:
        user_id (str): The UUID of the user who placed the order.
        items (json): A list of menuitems in an order.
        date (datetime): The date and time when the order was placed.
        total (float): The total amount of the order.
        status (str): The current status of the order.
        user (relationship): Relationship to the user who placed the order.

    """

    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}

    MAX_RETRIES = 3
    RETRY_DELAY = 0.3

    VALID_STATUSES = ['pending',
                      'confirmed',
                      'preparing',
                      'ready',
                      'delivered',
                      'cancelled']

    user_id = db.Column(db.String(40),
                        db.ForeignKey('users.id'),
                        nullable=False)
    items = db.Column(db.JSON, default={})
    date = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user = relationship("User", back_populates="orders")

    def validate(self):
        """Validate order data before saving."""
        if self.total <= 0:
            raise ValueError("Order total must be greater than zero")

        if not self.items:
            raise ValueError("Order must have at least one item")

        if self.date > datetime.now(UTC):
            raise ValueError("Order date cannot be in the future")

        if self.status not in self.VALID_STATUSES:
            raise SQLAlchemyError(f"Invalid status: {self.status}")

    def save(self):
        """Save the order to database with validation."""
        self.validate()
        return super().save()

    def update(self, **kwargs):
        """
        Update the order with retry mechanism for concurrent updates.

        Args:
            **kwargs: Attributes to update

        Returns:
            bool: True if update successful

        Raises:
            SQLAlchemyError: If update fails after all retries
        """
        retries = 0
        last_error = None

        while retries < self.MAX_RETRIES:
            try:
                # Update attributes
                for key, value in kwargs.items():
                    setattr(self, key, value)

                # Validate if status is being updated
                if 'status' in kwargs:
                    if kwargs['status'] not in self.VALID_STATUSES:
                        e = f"Invalid status: {kwargs['status']}"
                        raise SQLAlchemyError(e)

                # Attempt to commit
                db.session.commit()
                return True

            except SQLAlchemyError as e:
                last_error = e
                db.session.rollback()
                retries += 1

                if retries < self.MAX_RETRIES:
                    sleep(self.RETRY_DELAY)
                    continue

                raise last_error

    def __repr__(self):
        """
        Provide a string representation of the Order object.

        Returns:
            str: A string representation of the Order.
        """
        return f'<Order {self.id} by User {self.user_id}>'
