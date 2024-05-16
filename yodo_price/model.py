from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from yodo_price.constants import format_price


class Url(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str


class Price(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    price: int

    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product: Optional["Product"] = Relationship(back_populates="price_history")

    def format(self) -> str:
        return f"{self.id} | 取得日: {self.date.strftime('%Y-%m-%d %H:%M:%S')}| 価格: {format_price(self.price)} | 商品名: {self.product.name}"


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    image: str
    product_id: str = Field(index=True)
    price_history: List[Price] = Relationship(back_populates="product")


class LatestPrice(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: str
    name: str
    price: int
    date: datetime

    def format(self) -> str:
        return f"{self.id} | 取得日: {self.date.strftime('%Y-%m-%d %H:%M:%S')}| 価格: {self.price:,}円 | 商品名: {self.name}"
