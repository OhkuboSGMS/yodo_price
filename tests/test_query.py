from yodo_price.model import LatestPrice

from yodo_price.query import latest_price_query


def test_latest_price_query(session):
    query = latest_price_query
    result = session.exec(query).all()
    assert len(result) == 2
    result = list(map(LatestPrice.from_orm, result))
    assert result[0].name == "自転車"
    assert result[0].price == 500
    assert result[1].name == "炊飯器"
    assert result[1].price == 3000
    "\n".join(map(str, result))
