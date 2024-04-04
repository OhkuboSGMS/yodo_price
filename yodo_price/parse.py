from urllib.parse import urlparse

from bs4 import BeautifulSoup
from more_itertools import first

from yodo_price.constants import PriceType


def get_product_id(url: str) -> str:
    parsed_url = urlparse(url)
    path = list(filter(len, parsed_url.path.split("/")))
    return path[-1]


def get_product_image(soup: BeautifulSoup) -> str:
    modal = soup.find("div", id="pImgCell")
    image = first(modal.find_all("img", id="mainImg"), None)
    if not image:
        raise Exception("画像が取得できませんでした")
    return image["src"]


def get_product_price(soup: BeautifulSoup) -> int:
    price = first(soup.find_all("span", class_="productPrice"), None)
    if price:
        price_with_yen = price.text
        # ￥と,を削除
        price_without_yen = price_with_yen.replace("￥", "").replace(",", "")
        return int(price_without_yen)

    # 価格が取得できなかった場合、販売が終了している可能性がある
    sale_info = first(soup.find_all("div", class_="salesInfo"), None)
    sale_info = sale_info.text if sale_info else None

    if sale_info is None:
        raise Exception("価格が取得できませんでした")
    if sale_info == "販売を終了しました":
        return PriceType.END

    raise Exception("価格が取得できませんでした")


def get_product_name(soup: BeautifulSoup):
    title = soup.find("h1", id="products_maintitle")
    if not title:
        raise Exception("商品名が取得できませんでした")
    return title.text
