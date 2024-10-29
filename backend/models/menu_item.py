#!/usr/bin/env python3
"""Defines MenuItem model with admin operations"""
from app import db
from .base_model import BaseModel
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user

class MenuItem(BaseModel):
    """
    Represents a menu item in the system.

    This class defines the structure of MenuItem objects, including their
    optional toppings and category, with admin-specific operations.

    Attributes:
        name (str): The name of the menu item
        description (str): A detailed description of the menu item
        price (float): The base price of the menu item
        image_url (str): URL to the menu item's image
        is_available (bool): Whether the item is currently available
        toppings (list): Optional list of available toppings
        category (str): The category this item belongs to (e.g., "Burgers", "Drinks")
    """

    __tablename__ = "menu_items"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    toppings = db.Column(ARRAY(db.String), default=[])
    category = db.Column(db.String(50), nullable=False)

    @classmethod
    def create_menu_item(cls, **kwargs):
        """
        Create a new menu item (admin only).

        Returns:
            MenuItem: The created menu item

        Raises:
            ValueError: If required fields are missing or invalid
            PermissionError: If user is not an admin
        """
        if not current_user.is_admin:
            raise PermissionError("Only admins can create menu items")

        required_fields = ['name', 'price', 'category']
        if not all(field in kwargs for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields}")

        if kwargs.get('price', 0) <= 0:
            raise ValueError("Price must be greater than 0")

        menu_item = cls(**kwargs)
        menu_item.save()
        return menu_item

    @classmethod
    def update_menu_item(cls, item_id, **kwargs):
        """
        Update an existing menu item (admin only).

        Returns:
            MenuItem: The updated menu item

        Raises:
            ValueError: If item doesn't exist or updates are invalid
            PermissionError: If user is not an admin
        """
        if not current_user.is_admin:
            raise PermissionError("Only admins can update menu items")

        menu_item = cls.get_by_id(item_id)
        if not menu_item:
            raise ValueError("Menu item not found")

        if 'price' in kwargs and kwargs['price'] <= 0:
            raise ValueError("Price must be greater than 0")

        menu_item.update(**kwargs)
        return menu_item

    @classmethod
    def delete_menu_item(cls, item_id):
        """
        Delete a menu item (admin only).

        Raises:
            ValueError: If item doesn't exist
            PermissionError: If user is not an admin
        """
        if not current_user.is_admin:
            raise PermissionError("Only admins can delete menu items")

        menu_item = cls.get_by_id(item_id)
        if not menu_item:
            raise ValueError("Menu item not found")

        menu_item.delete()

    def to_dict(self):
        """Convert the menu item to a dictionary"""
        return {
            **super().to_dict(),
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'toppings': self.toppings,
            'category': self.category
        }

    def __repr__(self):
        """Provide a string representation of the MenuItem object."""
        return f'<MenuItem {self.name} (ID: {self.id})>'
