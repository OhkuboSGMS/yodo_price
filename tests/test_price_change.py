from yodo_price import check
from yodo_price import get
from tests.dummy_html import with_price

from sqlmodel import select
from yodo_price.model import Product


def test_price_is_lower(session):
    product = get.get_product("https://www.yodobashi.com/product/100000001000193273/", with_price(200))
    products = session.exec(select(Product)).all()
    product_A: Product = products[0]
    assert product_A.name == "自転車"
    assert check.is_price_lower(session, product_A, product["price"])
