import os

import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select
from yodo_price.get import get_product
from yodo_price.model import Product
from yodo_price.update import add_url
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
engine = create_engine(f"sqlite:///{os.environ['DB_NAME']}")
SQLModel.metadata.create_all(engine)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def add(ctx, url: str):
    """Adds two numbers together."""
    try:
        with Session(engine) as session:
            _ = get_product(url)
            add_url(url, session)
    except Exception as e:
        print(e)
        await ctx.send(f"add failed:{e}")
        return
    await ctx.send(f"{url} を登録しました")


@bot.command()
async def list(ctx):
    try:
        with Session(engine) as session:
            products: list[Product] = session.exec(select(Product).order_by(Product.id)).all()
            product_msgs = list(map(lambda p: f"{p.name}", products))
    except Exception as e:
        print(e)
        await ctx.send(f"list failed:{e}")
        return
    await ctx.send("登録済み商品一覧\n" + "\n".join(product_msgs))


bot.run(os.environ["DISCORD_BOT_TOKEN"])
