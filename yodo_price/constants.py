from enum import IntEnum


class PriceType(IntEnum):
    # 販売終了
    END = -2


def format_price(price: int) -> str:
    if price == PriceType.END:
        return "販売終了"
    return f"{price:,}円"
