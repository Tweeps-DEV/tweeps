#!/usr/bin/env python3
"""Defines the User model"""
from .base_model import BaseModel
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class User(BaseModel):
    """Defines a User model. Inherits from Base
    and BaseModel
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(60),  unique=True, nullable=False)
    phone_contact: Mapped[str] = mapped_column(String(15))
    password_hash: Mapped[str] = mapped_columns(String(60), nullable=False)
    address: Mapped[str] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    orders: Mapped[List["Order"]] = relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    @staticmethod
    def is_valid_email(email):
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_regex.match(email))
