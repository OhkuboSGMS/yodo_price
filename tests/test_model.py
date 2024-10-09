from yodo_price.model import Url, Product
from sqlmodel import select


def test_add_product(session):
    url = Url(url="https://www.yodobashi.com/product/100000001001357243/")

    session.add(url)
    session.commit()
    session.refresh(url)
    product = Product(
        id=url.id,
        name="パナソニック Panasonicアルカリ乾電池 EVOLTA（エボルタ） 単3形 8＋2本パック LR6EJSP/10S",
        product_id="100000001001357243",
        image="",
        enable=False,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    query_product = session.exec(
        select(Product).where(Product.product_id == "100000001001357243")
    ).one()

    assert query_product.name == product.name
    assert not query_product.enable
