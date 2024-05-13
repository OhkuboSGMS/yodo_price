from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from yodo_price.parse import get_product_price, get_product_name, get_product_image, get_product_id


def _get_from_yodobashi(url: str) -> requests.Response:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    return response


def get_product(url: str, html: Optional[str] = None) -> Dict:
    if html:
        response = html
    else:
        response = _get_from_yodobashi(url).text
    soup = BeautifulSoup(response, "html.parser")
    soup = soup.body
    price = get_product_price(soup)
    name = get_product_name(soup)
    img_url = get_product_image(soup)
    product_id = get_product_id(url)
    return {
        "price": price,
        "name": name,
        "img_url": img_url,
        "product_id": product_id
    }
