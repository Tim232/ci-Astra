import re

import bs4 as bs4
import discord
from discord.ext import commands
import requests

import astra
from astra import AstraContext
from libs.formatting import format_code, limit, html_to_md


class Python(commands.Cog):
    def __init__(self, bot: astra.AstraBot):
        self.bot = bot
        self.bot.logger.info("python:Downloading pages")
        self.builtins = requests.get("https://docs.python.org/3/library/functions.html").text
        self.bi_soup = bs4.BeautifulSoup(self.builtins, features="html.parser")
        self.glossary = requests.get("https://docs.python.org/3/glossary.html").text
        self.gl_soup = bs4.BeautifulSoup(self.glossary, features="html.parser")

    @property
    def description(self) -> str:
        return "Look up Python documentation"

    @commands.command(brief="Look up a python module")
    async def pymodule(self, ctx, *, name):
        try:
            module = __import__(name)
        except:  # noqa e722
            await ctx.send("That module isn't found")
            return
        await ctx.send(
            embed=discord.Embed(
                title=f"{name} Docs",
                description=format_code(limit(module.__doc__, 800, "....")),
                url=f"https://docs.python.org/3/library/{name}.html"
            )
        )

    @commands.command(brief="Look up the docs for a function")
    async def pydoc(self, ctx, *, name):
        try:
            sa = name.split(".")
            a = __import__(sa[0])  # import base module
            for i in sa[1:]:
                if i in a.__dict__:
                    a = a.__dict__[i]
                else:
                    a = a.__class__.__dict__[i]
        except:  # noqa e722
            await ctx.send("That function isn't found")
            return
        await ctx.send(
            embed=discord.Embed(
                title=f"{name} Docs",
                description=format_code(limit(a.__doc__, 800, "....")) if a.__doc__ else
                "No documentation available",
                url=f"https://docs.python.org/3/library/{sa[0]}.html#{name}" if a.__doc__ else None
            )
        )

    @commands.command(aliases=["pyprim"], brief="Look up the docs for a python primitive")
    async def pyprimitive(self, ctx, name: str):
        classes = {
            "dict": dict,
            "list": list,
            "int": int,
            "float": float,
            "string": str,
            "str": str,
            "bytearray": bytearray,
            "bytes": bytes
        }
        await ctx.send(
            embed=discord.Embed(
                title=f"{name} Docs",
                description=format_code(limit(classes[name].__doc__, 800, "....")) if name in classes else
                "Primitive not found",
                url=f"https://docs.python.org/3/library/functions.html#{name}"
            )
        )

    @commands.command(aliases=["pybi"], brief="Look up the docs for a python builtin")
    async def pybuiltin(self, ctx, name: str):
        try:
            ele: bs4.element.Tag = self.bi_soup.find_all("dt", attrs={"id": name})[0]
        except:  # noqa e722
            await ctx.send("No built-in found")
            return
        par: bs4.element.Tag = ele.parent
        ch = [n for n in par.children if n != "\n"]
        desc = f"""
    Type: {par.get("class")[0]}
    Usage: `{re.sub(r"[^ -~]", "", ele.text)}`
    Docs: {limit(html_to_md(str(ch[1]), "https://docs.python.org/3/library/", icode_links=True), 700)}
    """
        await ctx.send(
            embed=discord.Embed(
                title=f"Built-in {name}",
                description=desc,
                url=f"https://docs.python.org/3/library/functions.html#{name}"
            )
        )

    @commands.command(aliases=["pydef"], brief="Look up the definition for a python term")
    async def pydefine(self, ctx, *, name: str):
        try:
            ele: bs4.element.Tag = self.gl_soup.find_all(
                "dt", attrs={"id": "term-" + "-".join(name.lower().split(" "))})[0]
        except:  # noqa e722
            await ctx.send("No definition found")
            return
        nx: bs4.element.Tag = ele.next_sibling
        desc = f"""{limit(html_to_md(str(nx), "https://docs.python.org/3/library/", icode_links=True), 700)}"""
        await ctx.send(
            embed=discord.Embed(
                title=f"{name} definition",
                description=desc
            )
        )


def setup(bot: astra.AstraBot) -> None:
    bot.add_cog(Python(bot))
