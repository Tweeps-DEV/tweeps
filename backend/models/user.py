#!/usr/bin/env python3
"""Defines a user model"""
from .base_model import BaseModel
from .order import Order
from app import bcrypt, db
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

    __tablename__ = "users"

    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    phone_contact = db.Column(db.String(15))
    password_hash = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship("Order", back_populates="user")

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the user's stored password hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def is_valid_email(email):
        """Validate an email address."""
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_regex.match(email))

    def __repr__(self):
        """Provide a string representation of the User object."""
        return f'<User {self.username} (ID: {self.id})>'
