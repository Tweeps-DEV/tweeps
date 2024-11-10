#!/usr/bin/env python3
"""Cart model module for managing user shopping carts.

This module defines the Cart class that handles shopping cart functionality
including item management, price calculations, and validation. It provides
methods for adding, removing, and modifying cart items while maintaining
data integrity and proper error handling.
"""
import logging
from app import db
from datetime import datetime, UTC
from models.base_model import BaseModel
from models.menu_item import MenuItem
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class Cart(BaseModel):
    """Shopping cart model for managing user selections.

    Handles the storage and manipulation of items selected by users,
    including quantity management, price calculations, and data validation.
    Implements proper error handling and logging for all operations.

    Attributes:
        user_id: Reference to the cart owner
        items: JSON storage of selected menu items and quantities
        total_price: Running total of all items in cart
        last_modified: Timestamp of last cart modification
        user: Relationship to the cart owner
    """

    __tablename__ = "carts"
    __table_args__ = (
        db.Index('idx_cart_user', 'user_id'),
        {'extend_existing': True}
    )

    MAX_ITEMS_PER_PRODUCT = 99
    MIN_QUANTITY = 1

    user_id = db.Column(
        db.String(40),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    items = db.Column(db.JSON, default=dict, nullable=False)
    total_price = db.Column(db.Float, default=0.0, nullable=False)
    last_modified = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    user = relationship(
        "User",
        backref=db.backref("cart", uselist=False, cascade="all, delete-orphan"),
        lazy='joined'
    )

    def __init__(self, **kwargs):
        """Initialize cart with empty items if not provided."""
        if 'items' not in kwargs:
            kwargs['items'] = {}
        if 'total_price' not in kwargs:
            kwargs['total_price'] = 0.0
        super().__init__(**kwargs)

    def validate(self):
        """Validate cart data before save.

        Checks:
        - Items structure validity
        - Quantity limits
        - Price non-negativity
        - Item existence and availability

        Raises:
            ValueError: If any validation check fails
        """
        if not isinstance(self.items, dict):
            raise ValueError("Items must be a dictionary")

        if self.total_price < 0:
            raise ValueError("Total price cannot be negative")

        for item_id, details in self.items.items():
            if not isinstance(details, dict):
                raise ValueError(f"Invalid item structure for item {item_id}")

            if "quantity" not in details:
                raise ValueError(f"Missing quantity for item {item_id}")

            quantity = details["quantity"]
            if not isinstance(quantity, int):
                raise ValueError(f"Quantity must be an integer for item {item_id}")

            if not self.MIN_QUANTITY <= quantity <= self.MAX_ITEMS_PER_PRODUCT:
                raise ValueError(
                    f"Quantity must be between {self.MIN_QUANTITY} and "
                    f"{self.MAX_ITEMS_PER_PRODUCT} for item {item_id}"
                )

            # Verify item exists and is available
            menu_item = MenuItem.get_by_id(item_id)
            if not menu_item:
                raise ValueError(f"Menu item {item_id} not found")
            if not menu_item.is_available:
                raise ValueError(f"Menu item {item_id} is not available")

    def add_item(self, menu_item_id: str, quantity: int = 1,
                 selected_toppings: List[str] = None) -> None:
        """Add an item to the cart or update its quantity if it exists.

        Args:
            menu_item_id: ID of the menu item to add
            quantity: Number of items to add (default: 1)
            selected_toppings: List of topping names selected for this item

        Raises:
            ValueError: If item not found, unavailable, or quantity invalid
            SQLAlchemyError: If database operation fails
        """
        try:
            menu_item = MenuItem.get_by_id(menu_item_id)
            if not menu_item:
                raise ValueError("Menu item not found")
            if not menu_item.is_available:
                raise ValueError("Menu item is not available")
            if not self.MIN_QUANTITY <= quantity <= self.MAX_ITEMS_PER_PRODUCT:
                raise ValueError(
                    f"Quantity must be between {self.MIN_QUANTITY} and "
                    f"{self.MAX_ITEMS_PER_PRODUCT}"
                )

            with self.transaction():
                current_quantity = self.items.get(menu_item_id, {}).get("quantity", 0)
                new_quantity = current_quantity + quantity

                if new_quantity > self.MAX_ITEMS_PER_PRODUCT:
                    raise ValueError(f"Cannot exceed {self.MAX_ITEMS_PER_PRODUCT} items per product")

                self.items[menu_item_id] = {
                    "quantity": new_quantity,
                    "toppings": selected_toppings or []
                }

                self._update_total()
                self.save()

        except SQLAlchemyError as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            raise

    def remove_item(self, menu_item_id: str, quantity: Optional[int] = None) -> None:
        """Remove an item from the cart entirely or reduce its quantity.

        Args:
            menu_item_id: ID of the menu item to remove
            quantity: Number of items to remove (if None, removes all)

        Raises:
            ValueError: If item not in cart or quantity invalid
            SQLAlchemyError: If database operation fails
        """
        try:
            if menu_item_id not in self.items:
                raise ValueError("Item not in cart")

            with self.transaction():
                current_quantity = self.items[menu_item_id]["quantity"]

                if quantity is None or quantity >= current_quantity:
                    del self.items[menu_item_id]
                else:
                    if quantity < 1:
                        raise ValueError("Quantity to remove must be positive")
                    self.items[menu_item_id]["quantity"] -= quantity

                self._update_total()
                self.save()

        except SQLAlchemyError as e:
            logger.error(f"Error removing item from cart: {str(e)}")
            raise

    def update_item_quantity(self, menu_item_id: str, quantity: int) -> None:
        """Update the quantity of an item in the cart.

        Args:
            menu_item_id: ID of the menu item to update
            quantity: New quantity to set

        Raises:
            ValueError: If item not in cart or quantity invalid
            SQLAlchemyError: If database operation fails
        """
        try:
            if menu_item_id not in self.items:
                raise ValueError("Item not in cart")

            if not self.MIN_QUANTITY <= quantity <= self.MAX_ITEMS_PER_PRODUCT:
                raise ValueError(
                    f"Quantity must be between {self.MIN_QUANTITY} and "
                    f"{self.MAX_ITEMS_PER_PRODUCT}"
                )

            with self.transaction():
                self.items[menu_item_id]["quantity"] = quantity
                self._update_total()
                self.save()

        except SQLAlchemyError as e:
            logger.error(f"Error updating item quantity: {str(e)}")
            raise

    def _update_total(self) -> None:
        """Update the total price of the cart based on current items.

        Includes calculations for both base prices and selected toppings.
        """
        total = 0.0
        try:
            for item_id, details in self.items.items():
                menu_item = MenuItem.get_by_id(item_id)
                if menu_item and menu_item.is_available:
                    item_price = menu_item.price
                    quantity = details["quantity"]

                    # Calculate topping prices
                    if details.get("toppings"):
                        topping_price = sum(
                            t.get("price", 0)
                            for t in menu_item.toppings
                            if t.get("name") in details["toppings"]
                        )
                        item_price += topping_price

                    total += item_price * quantity

            self.total_price = round(total, 2)
            self.last_modified = datetime.now(UTC)

        except Exception as e:
            logger.error(f"Error calculating cart total: {str(e)}")
            raise

    def clear(self) -> None:
        """Remove all items from the cart.

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with self.transaction():
                self.items = {}
                self.total_price = 0.0
                self.last_modified = datetime.now(UTC)
                self.save()

        except SQLAlchemyError as e:
            logger.error(f"Error clearing cart: {str(e)}")
            raise

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """Convert the cart to a dictionary with detailed item information.

        Args:
            exclude: Set of fields to exclude from the dictionary

        Returns:
            Dict containing cart data with detailed menu item information
        """
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
                        "item": menu_item.to_dict(),
                        "subtotal": round(
                            menu_item.price * details["quantity"], 2
                        )
                    }

        data['items'] = items_detail
        return data

    def __repr__(self) -> str:
        """Provide a string representation of the Cart object."""
        return f'<Cart {self.id} owned by User {self.user_id}>'
