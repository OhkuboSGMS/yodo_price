from yodo_price.get import get_product
from unittest.mock import patch


def test_get_from_network_unavailable(example_product_button_battery: str):
    # ネットワークが利用できない場合を想定できるかテスト
    with patch("requests.get") as mock_get:
        mock_get.side_effect = ConnectionError
        try:
            result = get_product(example_product_button_battery)
            assert False
        except ConnectionError:
            pass
