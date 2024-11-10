#!usr/bin/env python3
"""Defines an Order model"""
import uuid
from app import db
from datetime import datetime, timezone, UTC
from models.base_model import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from time import sleep
from typing import Optional, Any, Dict, List


class Order(BaseModel):
    """Customer order model with full order lifecycle management.

    Handles order creation, status updates, and relationship to users.
    Implements a state machine for order status transitions.

    Attributes:
        user_id: Reference to the ordering user
        items: JSON storage of ordered items and quantities
        date: Order placement timestamp
        total: Total order amount
        status: Current order status (pending, confirmed, etc.)
        notes: Additional order notes
        delivery_address: Delivery location
        user: Relationship to the ordering user
    """

    __tablename__ = "orders"
    __table_args__ = (
        db.Index('idx_order_user_status', 'user_id', 'status'),
        {'extend_existing': True}
    )

    class Status:
        PENDING = 'pending'
        CONFIRMED = 'confirmed'
        PREPARING = 'preparing'
        READY = 'ready'
        DELIVERED = 'delivered'
        CANCELLED = 'cancelled'

        @classmethod
        def values(cls) -> List[str]:
            return [
                cls.PENDING, cls.CONFIRMED, cls.PREPARING,
                cls.READY, cls.DELIVERED, cls.CANCELLED
            ]

    VALID_TRANSITIONS = {
        Status.PENDING: [Status.CONFIRMED, Status.CANCELLED],
        Status.CONFIRMED: [Status.PREPARING, Status.CANCELLED],
        Status.PREPARING: [Status.READY, Status.CANCELLED],
        Status.READY: [Status.DELIVERED, Status.CANCELLED],
        Status.DELIVERED: [],
        Status.CANCELLED: []
    }

    MAX_RETRIES = 3
    RETRY_DELAY = 0.3

    user_id = db.Column(db.String(40),
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    items = db.Column(db.JSON, default={}, nullable=False)
    date = db.Column(db.DateTime(timezone=True),
                     nullable=False,
                     server_default=func.now())
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    delivery_address = db.Column(db.String(255))

    user = db.relationship(
            "User",
            back_populates="orders",
            lazy='joined'
    )

    def __init__(self, **kwargs):
        """Initialize order with default status."""
        if 'status' not in kwargs:
            kwargs['status'] = self.Status.PENDING
        if 'date' not in kwargs:
            kwargs['date'] = datetime.now(UTC)
        super().__init__(**kwargs)

    def validate(self):
        """Validate order data before save.

        Checks:
        - Total amount validity
        - Items structure
        - Status validity
        - Item quantities

        Raises:
            ValueError: If any validation check fails
        """
        if self.total <= 0:
            raise ValueError("Order total must be greater than zero")

        if not self.items or not isinstance(self.items, dict):
            raise ValueError("Order must have valid items")

        if self.status not in self.Status.values():
            raise ValueError(f"Invalid status: {self.status}")

        # Validate items structure
        for item_id, details in self.items.items():
            if not isinstance(details, dict):
                raise ValueError(f"Invalid item details for item {item_id}")
            if 'quantity' not in details:
                raise ValueError(f"Missing quantity for item {item_id}")
            if details['quantity'] <= 0:
                raise ValueError(f"Invalid quantity for item {item_id}")

    def can_transition_to(self, new_status: str) -> bool:
        """Check if a status transition is valid.

        Args:
            new_status: Target status for transition

        Returns:
            bool: Whether transition is allowed
        """
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def update_status(self, new_status: str) -> bool:
        """Update order status with validation."""
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid status transition from {self.status} to {new_status}"
            )

        try:
            with self.transaction():
                self.status = new_status
                self.save()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating order status: {str(e)}")
            return False

    @classmethod
    def get_user_orders(cls, user_id: str, status: str = None) -> List['Order']:
        """Get orders for a specific user with optional status filter."""
        try:
            query = cls.query.filter_by(user_id=user_id, is_deleted=False)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(cls.date.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user orders: {str(e)}")
            return []

    def calculate_total(self) -> float:
        """Calculate the total order amount including toppings.

        Returns:
            float: Calculated total rounded to 2 decimal places

        Raises:
            ValueError: If menu items not found or quantities invalid
        """
        try:
            total = 0.0
            for item_id, details in self.items.items():
                menu_item = MenuItem.get_by_id(item_id)
                if not menu_item:
                    raise ValueError(f"Menu item {item_id} not found")

                quantity = details.get('quantity', 0)
                if quantity <= 0:
                    raise ValueError(f"Invalid quantity for item {item_id}")

                item_total = menu_item.price * quantity

                # Add topping prices if applicable
                if details.get("toppings"):
                    topping_price = sum(
                        t.get("price", 0)
                        for t in menu_item.toppings
                        if t.get("name") in details["toppings"]
                    )
                    item_total += topping_price * quantity

                total += item_total

            return round(total, 2)
        except Exception as e:
            logger.error(f"Error calculating order total: {str(e)}")
            raise

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """Enhanced dictionary conversion with detailed item information."""
        if exclude is None:
            exclude = set()

        data = super().to_dict(exclude)

        # Add detailed items information
        items_detail = {}
        if isinstance(self.items, dict):
            for item_id, details in self.items.items():
                menu_item = MenuItem.get_by_id(item_id)
                if menu_item:
                    items_detail[item_id] = {
                        **details,
                        "item": menu_item.to_dict()
                    }

        data['items'] = items_detail
        return data

    def __repr__(self) -> str:
        """
        Provide a string representation of the Order object.

        Returns:
            str: A string representation of the Order.
        """
        return f'<Order {self.id} by User {self.user_id}>'
