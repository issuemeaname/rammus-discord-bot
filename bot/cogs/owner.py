import collections
import importlib
import inspect
import json
import os
import sys

# import discord
from discord.ext import commands

import bot.checks
from bot.utils import clear_screen
from bot.utils import embed
from bot.utils import wrap


class Owner:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def load(self, ctx, *cog_names):
        title = (", ").join(map(str.title, cog_names))
        desc = "Successfully loaded"

        for cog_name in cog_names:
            cog = f"bot.cogs.{cog_name}"

            try:
                self.bot.load_extension(cog)
            except Exception as e:
                desc = (f"Loading failed\n\n"
                        f"{type(e).__name__}: {e}")
                break

        await ctx.send(embed=embed(title, desc))

    @commands.command(hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def unload(self, ctx, *cog_names):
        title = (", ").join(map(str.title, cog_names))
        desc = "Successfully unloaded"

        for cog_name in cog_names:
            cog = f"bot.cogs.{cog_name}"

            try:
                self.bot.unload_extension(cog)
            except Exception as e:
                desc = (f"Loading failed\n\n"
                        f"{type(e).__name__}: {e}")
                break

        await ctx.send(embed=embed(title, desc))

    @commands.command(hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def reload(self, ctx, *cog_names):
        title = (", ").join(map(str.title, cog_names))
        desc = "Successfully restarted!"

        for i, cog_name in enumerate(cog_names):
            if cog_name == "all":
                cog_name = "cogs"

                try:
                    self.bot.setup()
                except Exception as e:
                    desc = (f"Restarting failed\n\n"
                            f"{type(e).__name__}: {e}")
                    break
                else:
                    break
            else:
                cog_name = cog_name == "info" and "information" or cog_name
                cog = f"bot.cogs.{cog_name}"

                try:
                    self.bot.unload_extension(cog)
                    self.bot.load_extension(cog)
                except Exception as e:
                    desc = (f"Restarting failed\n\n"
                            f"{type(e).__name__}: {e}")
                    break

        await ctx.send(embed=embed(title, desc))

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

    @commands.command(name="cls", aliases=["clear"], hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def _cls(self, ctx):
        clear_screen("windows", "Rammus", "\n\n")

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

        await ctx.send(embed=embed(title, desc))

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
    @bot.checks.is_owner()
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
    @bot.checks.is_owner()
    async def _exec(self, ctx, *, command):
        try:
            exec(command)
        except Exception as e:
            result = f"Failure\n\n{type(e).__name}: {e}"
        else:
            result = "Success"

        await ctx.send(f"```py\n{result}\n```")

    @commands.command(hidden=True)
    @bot.checks.is_owner()
    async def reboot(self, ctx, *args):
        if "--no-embed" not in args:
            await ctx.send(embed=embed("Rebooting...",
                                       "This may take a while."))
        else:
            await ctx.send("`Rebooting...\nThis may take a while.`")

        await self.bot.log(embed=embed("Status", "Offline"), cause="Close",
                           log=self.bot.logs.status)

        # might vary for other people
        os.execl(sys.executable, sys.executable, self.bot.file)

    @commands.command(aliases=["exit"], hidden=True)
    @bot.checks.is_owner()
    async def close(self, ctx):
        await ctx.send(embed=embed(title=None, desc="Shutting down..."))
        await self.bot.log(embed=embed("Status", "Offline"), cause="Close",
                           log=self.bot.logs.status)

        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))
