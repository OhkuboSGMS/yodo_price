import os
from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select

from yodo_price import update
from yodo_price.get import get_product
from yodo_price.model import Product, Url, Price
from yodo_price.update import add_url

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
engine = create_engine(f"sqlite:///{os.environ['DB_NAME']}")
SQLModel.metadata.create_all(engine)

logger.add("yodo_price_bot.log", rotation="1 day", retention="7 days")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def add(ctx: Context, url: str):
    """Adds two numbers together."""
    if os.environ["DISCORD_CHANNEL_ID"] and ctx.channel.id != int(os.environ["DISCORD_CHANNEL_ID"]):
        await ctx.send(f"このチャンネルでは使用できません")
        return
    try:
        with Session(engine) as session:
            _ = get_product(url)
            url_model = add_url(url, session)
            url_list = [url_model.url]
            _, product, price = update.update(url_list, session)[0]
    except Exception as e:
        logger.exception(e)
        await ctx.send(f"add failed:{e}")
        return
    await ctx.send(f"{url} を登録しました\n 商品名: {product.name}\n価格:{price.price:,}円")


@bot.command(name="list")
async def _list(ctx):
    if os.environ["DISCORD_CHANNEL_ID"] and ctx.channel.id != int(os.environ["DISCORD_CHANNEL_ID"]):
        await ctx.send(f"このチャンネルでは使用できません")
        return
    try:
        with Session(engine) as session:
            products: list[tuple[Product, Url]] \
                = session.exec(select(Product, Url).where(Product.id == Url.id).order_by(Product.id)).all()
            product_msgs = list(map(lambda p: f"{p[0].name}:{p[1].url}", products))
    except Exception as e:
        logger.exception(e)
        await ctx.send(f"list failed:{e}")
        return
    await ctx.send("登録済み商品一覧\n" + "\n".join(product_msgs))


@bot.command(name="log")
async def _log(ctx, n: Optional[int] = 10):
    try:
        with Session(engine) as session:
            prices = session.exec(select(Price).order_by(Price.date.desc()).limit(n)).all()
            msgs = list(map(lambda p: f"{p.date}:{p.price}:{p.product.name}", prices))
            await ctx.send("直近価格\n" + "\n".join(msgs))
    except Exception as e:
        logger.exception(e)
        await ctx.send(f"log:{e}")
        return


bot.run(os.environ["DISCORD_BOT_TOKEN"])
