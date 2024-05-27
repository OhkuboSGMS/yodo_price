from datetime import timedelta

import pytest
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session
from yodo_price.model import *


def _add_test_data(session: Session):
    url = Url(url="https://www.yodobashi.com/product/example1")
    url2 = Url(url="https://www.yodobashi.com/product/example2")
    session.add_all([url, url2])
    session.commit()
    session.refresh(url)
    session.refresh(url2)
    product_A = Product(id=url.id, name="自転車", product_id="ip1303", image="")
    product_B = Product(id=url2.id, name="炊飯器", product_id="ip3920", image="")

    session.add_all([product_A, product_B])
    session.commit()
    session.refresh(product_A)
    session.refresh(product_B)

    now = datetime.now()
    prices_A = [
        Price(date=now - timedelta(seconds=30), price=300, product=product_A),
        Price(date=now - timedelta(seconds=20), price=400, product=product_A),
        Price(date=now - timedelta(seconds=10), price=500, product=product_A),
    ]
    session.add_all(prices_A)
    prices_B = [
        Price(date=now - timedelta(seconds=30), price=4000, product=product_B),
        Price(date=now - timedelta(seconds=20), price=3000, product=product_B),
    ]
    session.add_all(prices_B)
    session.commit()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _add_test_data(session)
        yield session
