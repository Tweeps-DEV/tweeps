#!/usr/bin/env python3
"""Defines the User model"""
from models.base_model import Base
from models.base_model import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class User(BaseModel, Base):
    """Defines a User model. Inherits from Base
    and BaseModel
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(60))
    password_hash: Mapped[str] = mapped_columns(String(60))
