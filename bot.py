import os
from typing import Optional

import discord
from discord import Interaction
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select
from yodo_price import query
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
    await bot.tree.sync()
    print('------')


@bot.tree.command(name="yodo_add", description="監視するURLを追加")
async def add(ctx: Interaction, url: str):
    """Adds two numbers together."""
    if os.environ["DISCORD_CHANNEL_ID"] and ctx.channel.id != int(os.environ["DISCORD_CHANNEL_ID"]):
        await ctx.response.send_message(f"このチャンネルでは使用できません")
        return
    with Session(engine) as session:
        try:
            _ = get_product(url)
            url_model = add_url(url, session)
            url_list = [url_model.url]
            _, product, price = update.update(url_list, session)[0]
        except Exception as e:
            logger.exception(e)
            await ctx.response.send_message(f"add failed:{e}")
            return
        await ctx.response.send_message(f"{url} を登録しました\n 商品名: {product.name}\n価格:{price.price:,}円")


@bot.tree.command(name="yodo_list", description="登録済み商品一覧")
async def _list(ctx: Interaction):
    if os.environ["DISCORD_CHANNEL_ID"] and ctx.channel.id != int(os.environ["DISCORD_CHANNEL_ID"]):
        await ctx.response.send_message(f"このチャンネルでは使用できません")
        return
    try:
        with Session(engine) as session:
            products: list[tuple[Product, Url]] \
                = session.exec(select(Product, Url).where(Product.id == Url.id).order_by(Product.id)).all()
            product_msgs = list(map(lambda p: f"{p[0].name}:{p[1].url}", products))
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"list failed:{e}")
        return
    await ctx.response.send_message("登録済み商品一覧\n" + "\n".join(product_msgs))


@bot.tree.command(name="yodo_log_price")
async def _log(ctx: Interaction, n: Optional[int] = 10):
    try:
        with Session(engine) as session:
            prices = session.exec(select(Price).order_by(Price.date.desc()).limit(n)).all()
            msgs = list(map(lambda p: f"{p.date}:{p.price}:{p.product.name}", prices))
            await ctx.response.send_message("直近価格\n" + "\n".join(msgs))
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"log:{e}")
        return


@bot.tree.command(name="yodo_latest_price", description="最新価格(商品別)")
async def latest_price(ctx: Interaction):
    try:
        with Session(engine) as session:
            result = query.get_latest_price(session)
            await ctx.response.send_message("最新価格\n" + "\n".join(map(lambda x: x.format(), result)))
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"latest_price:{e}")
        return


bot.run(os.environ["DISCORD_BOT_TOKEN"])
