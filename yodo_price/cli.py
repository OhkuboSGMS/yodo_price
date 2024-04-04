import os

import fire
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from yodo_price import update


def get(url: str):
    engine = create_engine(f"sqlite:///{os.environ['DB_NAME']}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        url, product, price = update.update([url], session)[0]
        message = f"商品名: {product.name}\n価格:{price.price:,}円\n確認日時:{price.date}\n{url}"
        print(message)

    session.commit()


def main():
    load_dotenv()
    fire.Fire(get)


if __name__ == '__main__':
    main()
