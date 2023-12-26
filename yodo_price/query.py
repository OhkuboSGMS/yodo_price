from sqlmodel import Session, select

from yodo_price.model import Product, Price


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
