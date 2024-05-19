from enum import IntEnum

BASE_URL = "https://www.yodobashi.com/product/"


class PriceType(IntEnum):
    # 販売終了
    END = -2


def format_price(price: int) -> str:
    if price == PriceType.END:
        return "販売終了"
    return f"{price:,}円"
