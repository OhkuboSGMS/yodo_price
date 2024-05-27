from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from yodo_price.constants import format_price, BASE_URL


def get_short_product_name(product_name: Optional[int]):
    category_info = str(product_name).find("[")
    if category_info:
        return product_name[:category_info]
    return product_name


def get_product_url(product_id: Optional[int]) -> str:
    return f"{BASE_URL}/{product_id}"


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
        return (
            f"{self.id} | 取得日: {self.date.strftime('%Y-%m-%d %H:%M:%S')}| 価格: {format_price(self.price)} |"
            f" 商品名: {get_short_product_name(self.product.name)} |[link]({get_product_url(self.product_id)})"
        )


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
        return (
            f"{self.id} | 取得日: {self.date.strftime('%Y-%m-%d %H:%M:%S')}| 価格: {format_price(self.price)} |"
            f" 商品名: {get_short_product_name(self.name)} |[link]({get_product_url(self.product_id)})"
        )
