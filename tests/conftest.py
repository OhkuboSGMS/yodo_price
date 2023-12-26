from datetime import timedelta

import pytest
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session
from yodo_price.model import *


def _add_test_data(session: Session):
    product_A = Product(name="自転車", product_id="ip1303", image="")
    product_B = Product(name="炊飯器", product_id="ip3920", image="")

    session.add_all([product_A, product_B])
    session.commit()
    session.refresh(product_A)
    session.refresh(product_B)

    now = datetime.now()
    prices_A = [Price(date=now - timedelta(seconds=30),
                      price=300,
                      product=product_A),
                Price(date=now - timedelta(seconds=20),
                      price=400,
                      product=product_A),
                Price(date=now - timedelta(seconds=10),
                      price=500,
                      product=product_A),
                ]
    session.add_all(prices_A)
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
