import os
from typing import Optional, Sequence

import discord
from discord import Interaction
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, select

from yodo_price import query, update, filters
from yodo_price.get import get_product
from yodo_price.model import Price, Product, Url
from yodo_price.update import add_url

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
engine = create_engine(f"sqlite:///{os.environ['DB_NAME']}")
SQLModel.metadata.create_all(engine)

logger.add("yodo_price_bot.log", rotation="1 day", retention="7 days")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()
    print("------")


@bot.tree.command(name="yodo_add", description="監視するURLを追加")
async def add(ctx: Interaction, url: str):
    """Adds two numbers together."""
    await ctx.response.defer()
    if os.environ["DISCORD_CHANNEL_ID"] and ctx.channel.id != int(
        os.environ["DISCORD_CHANNEL_ID"]
    ):
        await ctx.response.send_message("このチャンネルでは使用できません")
        return
    with Session(engine) as session:
        try:
            _ = get_product(url)
            url_model = add_url(url, session)
            url_list = [url_model.url]
            results, errors = update.update(url_list, session)
            _, product, price = results[0]
            if len(errors) > 0:
                await ctx.followup.send(f"add failed:{errors}")
                return
        except Exception as e:
            logger.exception(e)
            await ctx.followup.send(f"add failed:{e}")
            return
        await ctx.followup.send(
            f"{url} を登録しました\n 商品名: {product.name}\n価格:{price.price:,}円"
        )


@bot.tree.command(name="yodo_list", description="登録済み商品一覧")
async def _list(ctx: Interaction):
    if os.environ["DISCORD_CHANNEL_ID"] and ctx.channel.id != int(
        os.environ["DISCORD_CHANNEL_ID"]
    ):
        await ctx.response.send_message("このチャンネルでは使用できません")
        return
    try:
        with Session(engine) as session:
            products: Sequence[tuple[Product, Url]] = session.exec(
                select(Product, Url).where(Product.id == Url.id).order_by(Product.id)
            ).all()
            product_msgs = list(map(lambda p: f"{p[0].name}:{p[1].url}", products))
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"list failed:{e}")
        return
    await ctx.response.send_message("登録済み商品一覧\n" + "\n".join(product_msgs))


@bot.tree.command(name="yodo_log_price")
async def _log(
    ctx: Interaction,
    n: Optional[int] = 10,
    id: Optional[int] = None,
    display_mode: str = "normal",
):
    """
    直近の価格を取得
    :param ctx:
    :param n:
    :param id:
    :return:
    """
    try:
        with Session(engine) as session:
            if id:
                prices = session.exec(
                    select(Price)
                    .where(Price.product_id == id)
                    .order_by(Price.date.desc())
                    .limit(n)
                ).all()

                if display_mode == "diff":
                    prices = filters.unique_consecutive(prices, "price")
                await ctx.response.send_message(
                    "直近価格\n" + Price.simple_list_format(prices)
                )
            else:
                prices = session.exec(
                    select(Price).order_by(Price.date.desc()).limit(n)
                ).all()
                msgs = list(map(lambda p: p.format(), prices))
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
            await ctx.response.send_message(
                "最新価格\n" + "\n".join(map(lambda x: x.format(), result))
            )
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"latest_price:{e}")
        return


@bot.tree.command(name="yodo_enable", description="商品の監視を有効化")
async def _enable(ctx: Interaction, id: int):
    try:
        with Session(engine) as session:
            product = session.exec(
                select(Product).where(Product.id == id)
            ).one_or_none()
            if not product:
                await ctx.response.send_message(f"{id} は登録されていません")
                return
            if product.enable:
                await ctx.response.send_message(
                    f"{product.name} は既に有効化されています.そのため何もしません"
                )
                return
            product.enable = True
            session.add(product)
            session.commit()
            await ctx.response.send_message(f"{product.name} を有効化しました")
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"Error:enable:{e}")
        return


@bot.tree.command(name="yodo_disable", description="商品の監視を無効化")
async def _disable(ctx: Interaction, id: int):
    try:
        with Session(engine) as session:
            product = session.exec(
                select(Product).where(Product.id == id)
            ).one_or_none()
            if not product:
                await ctx.response.send_message(f"{id} は登録されていません")
                return

            product.enable = False
            session.add(product)
            session.commit()
            await ctx.response.send_message(f"{product.name} を無効化しました")
    except Exception as e:
        logger.exception(e)
        await ctx.response.send_message(f"Error:disable:{e}")
        return


bot.run(os.environ["DISCORD_BOT_TOKEN"])
