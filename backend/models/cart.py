#!/usr/bin/enbv python3
"""Defines the user's cart"""
from .base_model import BaseModel
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column

class Cart(BaseModel):
    """A user's cart"""
    __tablename__ = "cart"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
