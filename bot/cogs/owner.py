import collections
import importlib
import json
import os
import sys

# import discord
from discord.ext import commands

import bot.checks
from bot.utils import clear_screen
from bot.utils import create_embed
from bot.utils import wrap


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog_names = None

    def process_cog_name(self, cog_name):
        cog_name = cog_name.lower()

        # instead of this, iterate over the cogs directory and get all of the
        # valid cog names, then check if the name matches any of them
        if self.cog_names is None:
            self.cog_names = self.bot.cogs.copy()

        for cog in self.cog_names:
            cog = cog.lower()

            if cog.startswith(cog_name):
                return cog
        return False

    @commands.command(aliases=["load", "unload", "reload", "r"], hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def manipulate_cog(self, ctx, cog):
        cog = self.process_cog_name(cog)
        path = f"bot.cogs.{cog}"
        name = ctx.invoked_with == "r" and "reload" or ctx.invoked_with
        functions = {
            "load": self.bot.load_extension,
            "unload": self.bot.unload_extension,
            "reload": self.bot.reload_extension
        }
        function = functions.get(name)
        desc = f"Successfully {name}ed!"
        function(path)

        await ctx.send(embed=create_embed(title=cog.title(), desc=desc))

    @commands.command(aliases=["mention"], hidden=True)
    @bot.checks.is_owner()
    async def ping(self, ctx, name, *, message=None):
        name = name.lower()
        message = message or "DJ wants you for a sec"
        members = {
            "reborn": self.bot.get_user(429605988530782208)
        }

        try:
            member = members[name]
        except KeyError:
            return
        else:
            await ctx.send(f"{member.mention} DJ said \"{message}\"")

    @commands.command(hidden=True)
    @bot.checks.is_owner()
    async def reboot(self, ctx, *args):
        title = "Rebooting..."
        desc = "This may take a while."

        if "--no-embed" not in args:
            await ctx.send(embed=create_embed(title, desc))
        else:
            await ctx.send(f"`{title}\n{desc}`")

        await self.bot.log(embed=create_embed("Status", "Offline"),
                           cause=ctx.command.name.title(),
                           log=self.bot.logs.status)

        # might vary for other people
        os.execl(sys.executable, sys.executable, self.bot.file)

    @commands.command(aliases=["exit"], hidden=True)
    @bot.checks.is_owner()
    async def close(self, ctx):
        await ctx.send(embed=create_embed(title=None, desc="Shutting down..."))
        await self.bot.log(embed=create_embed("Status", "Offline"),
                           cause=ctx.command.name, log=self.bot.logs.status)

        await self.bot.logout()

    @commands.command(name="cls", aliases=["clear"], hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def _cls(self, ctx):
        clear_screen("windows", "Rammus", end="\n\n")

    @commands.command(name="dir", hidden=True)
    @bot.checks.is_owner()
    async def _dir(self, ctx, *, obj):
        try:
            obj = eval(obj)
        except NameError:
            attribs = f"That object does not exist"
        name = obj.__name__
        attribs = ("\n").join(dir(obj))

        await ctx.send(f"**{name}**")

        for block in wrap(attribs):
            await ctx.send(block)

    @commands.command(name="eval", hidden=True)
    @commands.is_owner()
    async def _eval(self, ctx, *, command):
        try:
            result = eval(command)
        except Exception as e:
            result = f"{type(e).__name__}: {e}"
        else:
            if isinstance(result, collections.Iterable):
                result = json.dumps(result, indent=4)
        finally:
            result = str(result)

        for block in wrap(result):
            await ctx.send(block)

    @commands.command(name="exec", hidden=True)
    @commands.is_owner()
    async def _exec(self, ctx, *, command):
        try:
            exec(command)
        except Exception as e:
            result = f"Failure\n\n{type(e).__name__}: {e}"
        else:
            result = "Success"

        await ctx.send(f"```py\n{result}\n```")

    @commands.command(name="import", hidden=True)
    @bot.checks.is_owner()
    async def _import(self, ctx, module_name):
        title = module_name.title()
        desc = "Successfully imported!"

        try:
            globals()[module_name] = importlib.import_module(module_name)
        except Exception as e:
            desc = (f"Importing failed\n\n"
                    f"{type(e).__name__} - {e}")

        await ctx.send(embed=create_embed(title, desc))


def setup(bot):
    bot.add_cog(Owner(bot))
