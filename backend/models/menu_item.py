#!/usr/bin/env python3
"""Defines Menu Items"""
from .base_model import BaseModel
from sqlalchemy import Float, String, Boolean
from sqlalchemy import Mapped, mapped_column


class MenuItem(BaseModel):
    """A product tweeps offers"""
    __tablename__ = "menu_items"

    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(60))
    image_url: Mapped[str] = mapped_column(String(255))
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint('price >= 0', name='check_positive_price'),
    )
