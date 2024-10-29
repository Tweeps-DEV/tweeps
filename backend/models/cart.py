#!/usr/bin/enbv python3
"""Defines the user's cart"""
from app import db
from .base_model import BaseModel
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Cart(BaseModel):
    """
    Represents a cart in the system.

    This class defines the structure of Cart object.

    Attributes:
        items (dict): A dict of menu items picked by user
        user_id (str): An uuid str identifying the owner of the cart
        total_price (float): total price of the menuitems prices
    """
    __tablename__ = "carts"

    user_id = db.Column(db.String(40), ForeignKey('users.id'), nullable=False)
    items = db.Column(db.JSON, default={})
    total_price = db.Column(db.Float, default=0.0, nullable=False)

    def add_item(self, menu_item_id, quantity=1, selected_toppings=None):
        """
        Add an item to the cart or update its quantity if it exists.

        Args:
            menu_item_id: ID of the menu item to add
            quantity: Number of items to add (default: 1)
            selected_toppings: List of toppings selected for this item
        """
        menu_item = MenuItem.get_by_id(menu_item_id)
        if not menu_item:
            raise ValueError("Menu item not found")

        if not menu_item.is_available:
            raise ValueError("Menu item is not available")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Initialize or update item in cart
        if menu_item_id in self.items:
            self.items[menu_item_id]["quantity"] += quantity
        else:
            self.items[menu_item_id] = {
                "quantity": quantity,
                "toppings": selected_toppings or []
            }

        self._update_total()
        self.save()

    def remove_item(self, menu_item_id, quantity=None):
        """
        Remove an item from the cart entirely or reduce its quantity.

        Args:
            menu_item_id: ID of the menu item to remove
            quantity: Number of items to remove (if None, removes all)
        """
        if menu_item_id not in self.items:
            return

        if quantity is None or quantity >= self.items[menu_item_id]["quantity"]:
            del self.items[menu_item_id]
        else:
            self.items[menu_item_id]["quantity"] -= quantity

        self._update_total()
        self.save()

    def _update_total(self):
        """Update the total price of the cart"""
        total = 0
        for item_id, details in self.items.items():
            menu_item = MenuItem.get_by_id(item_id)
            if menu_item:
                total += menu_item.price * details["quantity"]
        self.total_price = total

    def clear(self):
        """Remove all items from the cart"""
        self.items = {}
        self.total_price = 0.0
        self.save()

    def to_dict(self):
        """Convert the cart to a dictionary with detailed item information"""
        items_detail = {}
        for item_id, details in self.items.items():
            menu_item = MenuItem.get_by_id(item_id)
            if menu_item:
                items_detail[item_id] = {
                    **details,
                    "item": menu_item.to_dict()
                }

        return {
            **super().to_dict(),
            'user_id': self.user_id,
            'items': items_detail,
            'total_price': self.total_price
        }

    def __repr__(self):
        """Provide a string representation of the Cart object."""
        return f'<Cart {self.id} owned by User {self.user_id}>'
