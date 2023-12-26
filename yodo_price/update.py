from datetime import datetime
from typing import List, Tuple

from sqlmodel import Session, select

from yodo_price.get import get_product
from yodo_price.model import Product, Price, Url


def update(url_list: List[str], session: Session) -> List[Tuple[str, Product, Price]]:
    """
    commitはしない
    """
    result = []
    for url in url_list:
        data = get_product(url)
        statement = select(Product).where(Product.product_id == data["product_id"])
        product = session.exec(statement).one_or_none()
        if not product:
            product = Product(name=data["name"], image=data["img_url"], product_id=data["product_id"])
            session.add(product)
            session.commit()
            session.refresh(product)
        price = Price(date=datetime.now(), price=data["price"], product=product)
        session.add(price)
        result.append((url, product, price))
    return result


def add_url(url: str, session: Session):
    _url = Url(url=url)
    session.add(_url)
    session.commit()
