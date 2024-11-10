#!/usr/bin/env python3
"""Defines MenuItem model with admin operations"""
from app import db
from flask_login import current_user
from models.base_model import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Any, Dict, List


class MenuItem(BaseModel):
    """Restaurant menu item model with full item details.

    Manages individual menu items including their properties, pricing,
    and administrative operations. Supports categorization and
    customization options.

    Attributes:
        name: Item name (2-100 characters)
        description: Detailed item description
        price: Item base price (between MIN_PRICE and MAX_PRICE)
        image_url: URL to item image
        is_available: Current availability status
        toppings: Available customization options
        category: Item category (e.g., "Burgers", "Drinks")
        preparation_time: Estimated preparation time in minutes
        calories: Caloric content
        allergens: List of allergen information
    """

    __tablename__ = "menu_items"

    MIN_PRICE = 0.01
    MAX_PRICE = 10000.00

    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    toppings = db.Column(db.JSON, default=list)
    category = db.Column(db.String(50), nullable=False, index=True)
    preparation_time = db.Column(db.Integer)  # in minutes
    calories = db.Column(db.Integer)
    allergens = db.Column(db.JSON, default=list)

    def validate(self):
        """Validate menu item data before save.

        Checks:
        - Name length and format
        - Price range
        - Category presence
        - Toppings structure and pricing

        Raises:
            ValueError: If any validation check fails
        """
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")

        if not self.MIN_PRICE <= self.price <= self.MAX_PRICE:
            raise ValueError(f"Price must be between {self.MIN_PRICE} and {self.MAX_PRICE}")

        if not self.category:
            raise ValueError("Category is required")

        if self.toppings is None:
            self.toppings = []

        if not isinstance(self.toppings, list):
            raise ValueError("Toppings must be a list")

        # Validate topping structure
        for topping in self.toppings:
            if not isinstance(topping, dict):
                raise ValueError("Each topping must be a dictionary")
            if 'name' not in topping:
                raise ValueError("Each topping must have a name")
            if 'price' not in topping:
                raise ValueError("Each topping must have a price")
            if not isinstance(topping['price'], (int, float)):
                raise ValueError("Topping price must be a number")
            if topping['price'] < 0:
                raise ValueError("Topping price cannot be negative")

    @classmethod
    def create_menu_item(cls, **kwargs) -> 'MenuItem':
        """
        Create a new menu item (admin only).

        Returns:
            MenuItem: The created menu item

        Raises:
            ValueError: If required fields are missing or invalid
            PermissionError: If user is not an admin
        """
        if not current_user or not current_user.is_admin:
            raise PermissionError("Only admins can create menu items")

        required_fields = {'name', 'price', 'category'}
        missing_fields = required_fields - set(kwargs.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            with cls.transaction():
                menu_item = cls(**kwargs)
                menu_item.validate()
                menu_item.save()
                return menu_item
        except SQLAlchemyError as e:
            logger.error(f"Error creating menu item: {str(e)}")
            raise

    @classmethod
    def update_menu_item(cls, item_id, **kwargs) -> 'MenuItem':
        """
        Update an existing menu item (admin only).

        Returns:
            MenuItem: The updated menu item

        Raises:
            ValueError: If item doesn't exist or updates are invalid
            PermissionError: If user is not an admin
        """
        if not current_user or not current_user.is_admin:
            raise PermissionError("Only admins can update menu items")

        try:
            with cls.transaction():
                menu_item = cls.get_by_id(item_id)
                if not menu_item:
                    raise ValueError("Menu item not found")

                # Validate price specifically if it's being updated
                if 'price' in kwargs and not cls.MIN_PRICE <= kwargs['price'] <= cls.MAX_PRICE:
                    raise ValueError(f"Price must be between {cls.MIN_PRICE} and {cls.MAX_PRICE}")

                menu_item.update(**kwargs)
                return menu_item
        except SQLAlchemyError as e:
            logger.error(f"Error updating menu item: {str(e)}")
            raise

    @classmethod
    def get_by_category(cls, category: str, include_unavailable: bool = False) -> List['MenuItem']:
        """Get menu items by category."""
        try:
            query = cls.query.filter_by(is_deleted=False)
            if not include_unavailable:
                query = query.filter_by(is_available=True)
            return query.filter_by(category=category).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving menu items by category: {str(e)}")
            return []

    @classmethod
    def delete_menu_item(cls, item_id):
        """
        Delete a menu item (admin only).

        Raises:
            ValueError: If item doesn't exist
            PermissionError: If user is not an admin
        """
        if not current_user or not current_user.is_admin:
            raise PermissionError("Only admins can delete menu items")

        try:
            with cls.transaction():
                menu_item = db.session.get(cls, item_id)
                if not menu_item:
                    raise ValueError("Menu item not found")

                db.session.delete(menu_item)
                db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Error deleting menu item: {str(e)}")

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """Convert the menu item to a dictionary"""
        if exclude is None:
            exclude = set()

        data = super().to_dict(exclude)

        # Add computed fields if needed
        data['is_available'] = self.is_available and not self.is_deleted

        return data

    def __repr__(self) -> str:
        """Provide a string representation of the MenuItem object."""
        return f'<MenuItem {self.name} (ID: {self.id})>'
