from typing import Dict

import aiohttp
from discord import Webhook


async def discord_webhook(messages: Dict, url: str):
    """
    # https://discordpy.readthedocs.io/ja/latest/api.html#webhook
    :return:
    """
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        await webhook.send(**messages)
