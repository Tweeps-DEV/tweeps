#!/usr/bin/env python3
"""Defines MenuItem model with admin operations"""
from backend.base import db
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user


class MenuItem(db.Model):
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
        category (str): The category this item belongs to
        (e.g., "Burgers", "Drinks")
    """

    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    toppings = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    is_deal_of_the_day = db.Column(db.Boolean, default=False)

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

    @classmethod
    def get_deal_of_the_day(cls):
        return cls.query.filter_by(is_deal_of_the_day=True).first()

    @staticmethod
    def get_menu_items():
        categories = MenuItem.query.with_entities(MenuItem.category).distinct()
        menu_items = {}
        for category in categories:
            menu_items[category] = MenuItem.query.filter_by(category=category).all()
        return menu_items

    def to_dict(self):
        """Convert the menu item to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'toppings': self.toppings,
            'category': self.category,
            'is_deal_of_the_day': self.is_deal_of_the_day
        }

    def __repr__(self):
        """Provide a string representation of the MenuItem object."""
        return f'<MenuItem {self.name}>'
