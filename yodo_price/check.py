from sqlmodel import Session

from yodo_price.model import Product
from yodo_price.query import get_last_price


def is_price_lower(session: Session, product: Product, price: int) -> bool:
    latest_price = get_last_price(session, product)
    return latest_price > price
