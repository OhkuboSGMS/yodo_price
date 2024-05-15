from sqlalchemy import text
from sqlmodel import Session, select
from typing_extensions import List, Optional, Tuple

from yodo_price.model import Product, Price, LatestPrice

latest_price_query = text("""
with latest_price as(
    select product_id, max(date) as date,price
    from Price
    group by product_id
)
select Product.id,Product.product_id,product.name,latest_price.price,latest_price.date from Product
join latest_price on product.id = latest_price.product_id;
""")


def get_latest_price(session: Session) -> Tuple[LatestPrice]:
    result = session.exec(latest_price_query).all()
    return tuple(map(LatestPrice.from_orm, result))


def get_last_price(session: Session, product: Product) -> int:
    """
    DB内の最新の値段を取得する
    """
    statement = select(Price).where(Price.product_id == product.id).order_by(Price.date.desc()).limit(1)
    last_price = session.exec(statement).one_or_none()
    if last_price:
        return last_price.price
    else:
        return 0


def get_products_latest_price(session: Session) -> List[Tuple[Product, Optional[Price]]]:
    """
    DB内の最新の値段を取得する,UrlとProductを結合し、Priceをgroup byして最新の値段を取得する
    """
    products = session.exec(select(Product)).all()
    results = []
    for product in products:
        statement = select(Price).where(Price.product_id == product.id).order_by(Price.date.desc()).limit(1)
        last_price = session.exec(statement).one_or_none()
        if last_price:
            results.append((product, last_price))
        else:
            results.append((product, None))
    return results
