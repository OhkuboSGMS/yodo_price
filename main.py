import asyncio
import os
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select

from yodo_price import update
from yodo_price.check import is_price_change
from yodo_price.model import Url, get_product_url
from yodo_price.notify import discord_webhook
from yodo_price.query import get_products_latest_price, get_last_price
from yodo_price.upload import upload_gcp
from yodo_price.error import notify_discord_on_exception

"""
https://www.crummy.com/software/BeautifulSoup/bs4/doc/#
https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
"""


@notify_discord_on_exception("ヨドボットエラー", "DISCORD_WEBHOOK_URL")
async def main():
    engine = create_engine(f"sqlite:///{os.environ['DB_NAME']}")
    SQLModel.metadata.create_all(engine)

    """
    1. Urlテーブルから値段取得対象のURLを取得する
    2. URLから商品情報を取得する
    3. 取得時点での値段をPriceテーブルに保存する
    """
    with Session(engine) as session:
        url_list = session.exec(select(Url)).all()
        url_list = [u.url for u in url_list]
        # 直近の値段を取得
        result = get_products_latest_price(session)
        # 商品ページから最新化価格を取得しコミット
        _, errors = update.update(url_list, session)
        if errors:
            for error in errors:
                await discord_webhook(
                    {
                        "username": "ヨドボット",
                        "content": f"エラーが発生しました:{error}",
                    },
                    os.environ["DISCORD_WEBHOOK_URL"],
                )
        for product, last_price in result:
            if last_price is None:
                price: Optional[int] = None
            else:
                price: int = last_price.price
            if product.enable is False:
                # 通知をキャンセル
                continue

            # 安くなった場合のみ通知する
            if is_price_change(session, product, price):
                # 最新価格
                latest_price = get_last_price(session, product)
                # price -> 直近価格
                message = f"価格変化を検知:ID:{product.id} 商品名: {product.name}\nこれまで:{price:,}円,現在:{latest_price:,}円|[link]({get_product_url(product.product_id)})"
                await discord_webhook(
                    {"username": "ヨドボット", "content": message},
                    os.environ["DISCORD_WEBHOOK_URL"],
                )

        session.commit()


async def backup_db():
    blog_name = datetime.now().strftime("%Y_%m_%d")
    db_path = os.path.abspath(os.environ["DB_NAME"])
    upload_gcp(blog_name, db_path)
    print("Back up DB ")


async def schedule():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, "cron", hour="0,6,12,18", minute="0")
    scheduler.add_job(backup_db, "cron", hour=23, minute=59)
    scheduler.start()
    print("Press Ctrl+{0} to exit".format("Break" if os.name == "nt" else "C"))

    while True:
        await asyncio.sleep(1000)


if __name__ == "__main__":
    try:
        load_dotenv()
        loop = asyncio.get_event_loop()
        # 起動時に取得処理を一度実行
        loop.run_until_complete(main())
        loop.run_until_complete(schedule())
    except (KeyboardInterrupt, SystemExit):
        pass
