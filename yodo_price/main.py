import asyncio
import os
from datetime import datetime

from sqlmodel import SQLModel, create_engine, Session, select

from yodo_price.get import get_product
from yodo_price.model import Product, Price
from yodo_price.notify import discord_webhook

from dotenv import load_dotenv

from yodo_price import update

"""
https://www.crummy.com/software/BeautifulSoup/bs4/doc/#
https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
"""


async def main(url_list_file: str):
    engine = create_engine("sqlite:///product.db")
    SQLModel.metadata.create_all(engine)

    """
    1. Urlテーブルから値段取得対象のURLを取得する
    2. URLから商品情報を取得する
    3. 取得時点での値段をPriceテーブルに保存する
    """
    with Session(engine) as session:
        url_list = [m.strip() for m in open(url_list_file).readlines()]
        result = update.update(url_list, session)

        for url, product, price in result:
            message = f"商品名: {product.name}\n価格:{price.price:,}円\n確認日時:{price.date}\n{url}"
            print(message)
            await discord_webhook({"username": "ヨドボット",
                                   "content": message
                                   },
                                  os.environ["DISCORD_WEBHOOK_URL"])

    session.commit()


if __name__ == '__main__':
    load_dotenv()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main("list.txt"))
