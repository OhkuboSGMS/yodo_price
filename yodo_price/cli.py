import os

import fire
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select
from dotenv import load_dotenv

from yodo_price import update
from yodo_price.model import Url


def get(url: str):
    engine = create_engine(f"sqlite:///{os.environ['DB_NAME']}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        url, product, price = update.update([url], session)[0]
        message = f"商品名: {product.name}\n価格:{price.price:,}円\n確認日時:{price.date}\n{url}"
        print(message)

    session.commit()


if __name__ == '__main__':
    load_dotenv()
    fire.Fire()
