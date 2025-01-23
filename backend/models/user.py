#!/usr/bin/env python3
"""Defines a user model"""
import logging
import re
from app import bcrypt, db
from datetime import datetime,  UTC
from models.base_model import BaseModel
from models.order import Order

logger = logging.getLogger(__name__)


class User(BaseModel):
    """User account model with authentication and profile management.

    Handles user account data, authentication, and security measures.
    Implements password hashing and validation rules for user data.

    Attributes:
        username: Unique username (3-30 alphanumeric chars)
        email: Unique email address
        phone_contact: Optional phone number
        password_hash: Securely hashed password
        address: User's delivery address
        is_admin: Administrative privileges flag
        login_attempts: Failed login attempt counter
        last_login: Most recent login timestamp
        is_active: Account status flag
        orders: Relationship to user's orders
    """

    __tablename__ = "users"
    __table_args__ = (
        db.Index('idx_user_email_username', 'email', 'username'),
        {'extend_existing': True}
    )

    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_REGEX = re.compile(r'^\+?1?\d{9,15}$')

    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    phone_contact = db.Column(db.String(15))
    password_hash = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    login_attempts = db.Column(db.Integer, default=0, nullable=False)
    last_login = db.Column(db.DateTime(timezone=True))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    orders = db.relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )

    def validate(self):
        """Validate user data before save.

        Checks:
        - Username format (alphanumeric, 3-30 chars)
        - Email format
        - Phone number format (if provided)
        - Password hash presence

        Raises:
            ValueError: If any validation check fails
        """
        if not self.USERNAME_REGEX.match(self.username):
            raise ValueError("Invalid username format")

        if not self.EMAIL_REGEX.match(self.email):
            raise ValueError("Invalid email format")

        if self.phone_contact and not self.PHONE_REGEX.match(self.phone_contact):
            raise ValueError("Invalid phone number format")

        if not self.password_hash:
            raise ValueError("Password hash is required")

    def set_password(self, password: str) -> None:
        """Set the user's password with security requirements.

        Password must contain:
        - At least 8 characters
        - One uppercase letter
        - One lowercase letter
        - One number

        Args:
            password: Plain text password to hash

        Raises:
            ValueError: If password requirements not met
        """
        if password:
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")

            if not any(c.isupper() for c in password):
                raise ValueError("Password must contain at least one uppercase letter")

            if not any(c.islower() for c in password):
                raise ValueError("Password must contain at least one lowercase letter")

            if not any(c.isdigit() for c in password):
                raise ValueError("Password must contain at least one number")

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.password_hash = password_hash

    def check_password(self, password: str) -> bool:
        """Verify a password and handle login attempts.

        Implements login attempt tracking and lockout after 5 failed attempts.

        Args:
            password: Plain text password to verify

        Returns:
            bool: Whether password matches
        """
        try:
            if not password or not self.password_hash:
                return False

            if self.login_attempts and self.login_attempts >= 5:
                logger.warning(f"Too many login attempts for user {self.id}")
                return False

            is_valid = bcrypt.check_password_hash(self.password_hash, password)

            if not is_valid:
                self.login_attempts += 1
            else:
                self.login_attempts = 0
                self.last_login = datetime.now(UTC)
                self.save()

            return is_valid

        except Exception as e:
            logger.error(f"Error checking password: {str(e)}")
            return False

    def reset_login_attempts(self) -> None:
        """Reset failed login attempts."""
        self.login_attempts = 0
        self.save()

    def __repr__(self) -> str:
        """Provide a string representation of the User object."""
        return f'<User {self.username} (ID: {self.id})>'
