#!usr/bin/env python3
"""Defines an Order model"""
from .base_model import Base, BaseModel
from .menu_item import MenuItem
from .user import User
from sqlalchemy import Float, ForeignKey, relationship, String, Table
from sqlalchemy.orm import Mapped, mapped_column
from typing import List, Optional


order_items = Table(
    'order_items',
    Base.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('menu_item_id', ForeignKey('menu_items.id'), primary_key=True),
    Column('quantity', Integer)
)


class Order(BaseModel):
    """An Order made by a client"""
    __tablename__ = "orders"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    order_status: Mapped[str] = mapped_column(String(15), default="pending")

    items: Mapped[List["MenuItem"]] = relationship(secondary=order_items, back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")
