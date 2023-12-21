import asyncio
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select

from yodo_price import update
from yodo_price.model import Url
from yodo_price.notify import discord_webhook
from yodo_price.upload import upload_gcp

"""
https://www.crummy.com/software/BeautifulSoup/bs4/doc/#
https://zenn.dev/shimakaze_soft/articles/6e5e47851459f5
"""


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
        result = update.update(url_list, session)

        for url, product, price in result:
            message = f"商品名: {product.name}\n価格:{price.price:,}円\n確認日時:{price.date}\n{url}"
            print(message)
            await discord_webhook({"username": "ヨドボット",
                                   "content": message
                                   },
                                  os.environ["DISCORD_WEBHOOK_URL"])

    session.commit()


async def backup_db():
    blog_name = datetime.now().strftime("%Y_%m_%d")
    db_path = os.path.abspath(os.environ["DB_NAME"])
    upload_gcp(blog_name, db_path)
    print("Back up DB ")


async def schedule():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, "cron", hour="0,12", minute="0")
    scheduler.add_job(backup_db, "cron", day_of_week="sun", hour=23, minute=59)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    while True:
        await asyncio.sleep(1000)


if __name__ == '__main__':
    try:
        load_dotenv()
        loop = asyncio.get_event_loop()
        # loop.run_until_complete(main())
        loop.run_until_complete(schedule())
    except (KeyboardInterrupt, SystemExit):
        pass
