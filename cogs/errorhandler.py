import astra
import sys
import traceback

import discord
from discord.ext import commands
import sys
import traceback

import discord
from discord.ext import commands

import astra
from astra import AstraContext


class ErrorHandler(commands.Cog):
    def __init__(self, bot: astra.AstraBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: AstraContext, error):  # noqa: C901
        if hasattr(ctx.command, 'on_error'):
            return
        cog: commands.Cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound,)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
        if isinstance(error, commands.NSFWChannelRequired):
            await ctx.send_error("This command can only be used in NSFW channels")
        if isinstance(error, commands.DisabledCommand):
            await ctx.send_error(f'{ctx.command} has been disabled.')
        elif isinstance(error, (
                commands.NotOwner,
                commands.MissingPermissions,
                commands.BotMissingAnyRole,
                commands.MissingRole,
                commands.BotMissingPermissions
        )):
            await ctx.send_error(str(error))
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, discord.Forbidden):
            await ctx.send_error("I don't have the permissions for that")
        elif isinstance(error, commands.BadArgument):
            await ctx.send_error(str(error))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send_error(f"You are on cooldown. Try again in {round(error.retry_after)}s")
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot: astra.AstraBot) -> None:
    bot.add_cog(ErrorHandler(bot))
