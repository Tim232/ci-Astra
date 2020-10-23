import asyncio
import logging
from typing import Union, List

import aiohttp
import aiohttp.client_exceptions
import discord
from discord.ext import commands
from ruamel.yaml import YAML

from .astra_context import AstraContext
from .logging import LoggingHandler


class AstraBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.cog_groups = {}
        print("[BOT] Initializing bot")
        super(AstraBot, self).__init__(*args, **kwargs)

        self.TRACE = 7
        for logger in [
            "astra",
            "discord.client",
            "discord.gateway",
            "discord.http"
        ]:
            logging.getLogger(logger).setLevel(logging.DEBUG if logger == "astra" else logging.INFO)
            logging.getLogger(logger).addHandler(LoggingHandler())
        self.logger = logging.getLogger("astra")

    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=AstraContext)
        await self.invoke(ctx)

    async def start(self, *args, **kwargs):
        """|coro|
        A shorthand coroutine for :meth:`login` + :meth:`connect`.
        Raises
        -------
        TypeError
            An unexpected keyword argument was received.
        """
        bot = kwargs.pop('bot', True)
        reconnect = kwargs.pop('reconnect', True)
        if kwargs:
            raise TypeError("unexpected keyword argument(s) %s" % list(kwargs.keys()))

        for i in range(0, 6):
            try:
                self.logger.debug(f"bot:Connecting, try {i + 1}/6")
                await self.login(*args, bot=bot)
                break
            except aiohttp.client_exceptions.ClientConnectionError as e:
                self.logger.warning(f"bot:Connection {i + 1}/6 failed")
                self.logger.warning(f"bot:  {e}")
                self.logger.warning(f"bot: waiting {2 ** (i + 1)} seconds")
                await asyncio.sleep(2 ** (i + 1))
                self.logger.info("bot:attempting to reconnect")
        else:
            self.logger.critical("bot: failed after 6 attempts")
            return

        for cog in self.cogs:
            cog = self.get_cog(cog)
            if not cog.description and cog.qualified_name not in self.cog_groups["Hidden"]:
                self.logger.critical(f"bot:cog {cog.qualified_name} has no description")
                return

        missing_brief = []
        for command in self.commands:
            if not command.brief:
                missing_brief.append(command)

        if missing_brief:
            self.logger.error("bot:the following commands are missing help text")
            for i in missing_brief:
                self.logger.error(f"bot: - {i.cog.qualified_name}.{i.name}")
            return

        await self.connect(reconnect=reconnect)

        await self.connect(reconnect=reconnect)

    def find_cog(self, name: str, *,
                 allow_ambiguous=False,
                 allow_none=False,
                 check_description=False) -> Union[List[str], str]:
        found = []
        for c in self.cogs:
            if c.lower().startswith(name.lower()):
                found.append(c)
            if c.lower() == name.lower():
                found = [c]
                break
        if not found and not allow_none:
            raise commands.BadArgument(f"Module {name} not found.")
        if len(found) > 1 and not allow_ambiguous:
            raise commands.BadArgument(f"Name {name} can refer to multiple modules: "
                                       f"{', '.join(found)}. Use a more specific name.")
        return found

    def set_cog_group(self, cog: str, group: str):
        if group not in self.cog_groups:
            self.cog_groups[group] = [cog]
        else:
            self.cog_groups[group].append(cog)

    def load_extensions(self):
        with open("extensions.yaml") as fp:
            extensions = YAML().load(stream=fp)
        for grp_name in extensions:
            for path, cog_name in extensions[grp_name].items():
                try:
                    self.logger.info(f"cog:Loading {grp_name}:{cog_name} from {path}")
                    super(AstraBot, self).load_extension(path)
                except discord.ClientException as e:
                    self.logger.critical(f"An error occurred while loading {path}")
                    self.logger.critical(e.__str__().split(":")[-1].strip())
                    exit(1)
                except commands.ExtensionFailed as e:
                    self.logger.critical(f"An error occurred while loading {path}")
                    self.logger.critical(e.__str__().split(":")[-1].strip())
                    exit(1)
                self.set_cog_group(cog_name, grp_name)
