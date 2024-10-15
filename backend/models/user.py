#!/usr/bin/env python3
"""Defines the User model"""
from .base_model import BaseModel
from sqlalchemy import String
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
    is_admin: Mapped[bool] = mpped_column(default=False)
