#!/usr/bin/env python3
"""Defines a user model"""
from backend.extensions import bcrypt, db
from models.base_model import BaseModel
from models.order import Order
import re

class User(BaseModel):
    """
    Represents a user in the system.

    This class defines the structure and behavior of User objects, including
    authentication methods and data validation.

    Attributes:
        username (str): The user's username. Must be unique and non-null.
        email (str): The user's email address. Must be unique and non-null.
        phone_contact (str): The user's phone number.
        password_hash (str): The hashed password for the user. Non-null.
        address (str): The user's address.
        is_admin (bool): Indicates whether the user has admin privileges.
        orders (relationship): Relationship to the user's orders.
    """

    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the user's stored password hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Provide a string representation of the User object."""
        return f'<User {self.username} (ID: {self.id})>'
