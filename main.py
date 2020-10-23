import logging
import os

import dotenv
from discord.ext import commands

from astra import AstraBot

dotenv.load_dotenv()

logging.addLevelName(7, "TRACE")

bot = AstraBot(command_prefix="?", help_command=None)
bot.load_extensions()

@bot.event
async def on_ready():
    bot.logger.info("Astra online!")

bot.run(os.getenv("TOKEN"))
