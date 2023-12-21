import os

import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from yodo_price.get import get_product
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


bot.run(os.environ["DISCORD_BOT_TOKEN"])
