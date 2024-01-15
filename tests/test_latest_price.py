import pytest
from sqlmodel import select

from yodo_price.model import Product, Price
from more_itertools import first
from yodo_price.query import get_last_price


def test_can_get_latest_price(session):
    products = session.exec(select(Product)).all()
    product_A = products[0]
    assert product_A.name == "自転車"
    latest_price = get_last_price(session, product_A)
    assert latest_price == 500
