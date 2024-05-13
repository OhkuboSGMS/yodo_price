from sqlmodel import Session
from typing_extensions import Optional

from yodo_price.model import Product
from yodo_price.query import get_last_price


def is_price_lower(session: Session, product: Product, price: Optional[int]) -> bool:
    """

    :param session:
    :param product:
    :param price:更新前の価格
    :return:
    """
    latest_price = get_last_price(session, product)
    print(f"最新価格:{latest_price},更新前の価格:{price},商品名:{product.name}")
    if price is None:
        return False
    return latest_price < price
