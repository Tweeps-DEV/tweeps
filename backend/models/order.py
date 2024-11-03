#!usr/bin/env python3
"""Defines an Order model"""
import uuid
from backend.extensions import db  # Updated import
from models.base_model import BaseModel  # Updated import
from sqlalchemy.orm import relationship

class Order(BaseModel):
    """
    Represents an order in the system.

    This class defines the structure of Order objects and their relationship to Users.

    Attributes:
        user_id (str): The UUID of the user who placed the order.
        date (datetime): The date and time when the order was placed.
        total (float): The total amount of the order.
        status (str): The current status of the order.
        user (relationship): Relationship to the user who placed the order.

    """

    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}  # Add this line

    id = db.Column(db.Integer, primary_key=True)  # Add this line
    items = db.Column(db.PickleType, nullable=False)  # Updated type
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Updated type
    date = db.Column(db.DateTime, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user = relationship("User", back_populates="orders")

    def __repr__(self):
        """
        Provide a string representation of the Order object.

        Returns:
            str: A string representation of the Order.
        """
        return f'<Order {self.id} by User {self.user_id}>'
