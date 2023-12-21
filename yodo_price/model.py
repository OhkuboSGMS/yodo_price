from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Url(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str


class Price(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    price: int

    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product: Optional["Product"] = Relationship(back_populates="price_history")


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    image: str
    product_id: str = Field(index=True)
    price_history: List[Price] = Relationship(back_populates="product")
