import collections
import importlib
import io
import json
import textwrap
from contextlib import redirect_stdout

# import discord
from discord.ext import commands

import bot.checks
from bot.utils import clear_screen
from bot.utils import create_embed
from bot.utils import wrap


class Owner(commands.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot):
        self.bot = bot
        self.cog_names = None
        self.members = {
            "reborn": self.bot.get_user(429605988530782208),
            "chun": self.bot.get_user(202373732067442690),
        }
        self.cog_functions = {
            "load": self.bot.load_extension,
            "unload": self.bot.unload_extension,
            "reload": self.bot.reload_extension
        }

    @bot.checks.is_owner()
    @bot.checks.delete()
    async def cog_check(self, ctx):
        return True

    def process_cog_name(self, cog_name):
        cog_name = cog_name.lower()

        # instead of this, iterate over the cogs directory and get all of the
        # valid cog names, then check if the name matches any of them
        if self.cog_names is None:
            self.cog_names = self.bot.cogs.copy()

        for cog in self.cog_names:
            cog = cog.lower().replace(" ", "_")

            if cog.startswith(cog_name):
                return cog
        return False

    def setup_code(self, code):
        if code.startswith("```") and code.endswith("```"):
            code = ("\n").join(code.split("\n")[1:-1])

        indented = textwrap.indent(code, " "*4)
        function = (f"async def function():\n"
                    f"{indented}")

        return function

    async def process_shutdown(self, ctx, title=None, desc=None, *args):
        print(title)

        if title and desc is None:
            message = f"`{title}`"
        else:
            message = (f"`{title}\n"
                       f"{desc}`")

        if "--no-embed" not in args:
            await ctx.send(embed=create_embed(title, desc))
        else:
            await ctx.send(message)

        await self.bot.log(embed=create_embed("Status", "Offline"),
                           cause=ctx.command.name.title(),
                           log=self.bot.logs.status)

        await self.bot.close(ctx)

    @commands.command(aliases=["load", "unload", "reload", "r"])
    async def manipulate_cog(self, ctx, cog):
        cog = self.process_cog_name(cog)
        path = f"bot.cogs.{cog}"
        name = ctx.invoked_with == "r" and "reload" or ctx.invoked_with
        function = self.cog_functions.get(name)
        desc = f"Successfully {name}ed!"
        function(path)

        await ctx.send(embed=create_embed(title=cog.title(), desc=desc))

    @commands.command(hidden=True)
    async def reboot(self, ctx, *args):
        title = "Rebooting..."
        desc = "This may take a while."

        await self.process_shutdown(ctx, title, desc, *args)

    @commands.command(aliases=["exit"])
    async def close(self, ctx, *args):
        title = "Shutting down..."
        desc = None

        await self.process_shutdown(ctx, title, desc, *args)

    @commands.command(name="cls", aliases=["clear"])
    @commands.is_owner()
    async def _cls(self, ctx):
        clear_screen("windows", "Rammus", end="\n\n")

    @commands.command(name="dir")
    @commands.is_owner()
    async def _dir(self, ctx, *, obj):
        try:
            obj = eval(obj)
        except NameError:
            attribs = f"That object does not exist"
        name = type(obj).__name__
        attribs = ("\n").join(dir(obj))

        await ctx.send(f"**{name}**")

        for block in wrap(attribs):
            await ctx.send(block)

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        code = self.setup_code(code)
        stdout = io.StringIO()
        env = {
            **globals(),
            "self": self,
            "ctx": ctx
        }

        async with ctx.channel.typing():
            try:
                exec(code, env)
            except Exception as e:
                result = f"{type(e).__name__}: {e}"
            else:
                function = env.get("function")

                try:
                    with redirect_stdout(stdout):
                        result = await function()
                except Exception as e:
                    result = f"{type(e).__name__}: {e}"
                else:
                    if result is None:
                        result = stdout.getvalue()

                    if isinstance(result, collections.Iterable):
                        result = json.dumps(result, indent=4)
                finally:
                    if result == "\"\"":
                        result = None
                    result = str(result)

        for block in wrap(result):
            await ctx.send(block)

    @commands.command(name="exec")
    @commands.is_owner()
    async def _exec(self, ctx, *, code):
        code = self.setup_code(code)
        env = {
            "self": self,
            "ctx": ctx
        }

        env.update(globals())

        async with ctx.channel.typing():
            try:
                exec(code, env)
            except Exception as e:
                return await ctx.send(f"{type(e).__name__}: {e}")

            function = env.get("function")

            try:
                await function()
            except Exception as e:
                result = f"Failure\n\n{type(e).__name__}: {e}"
            else:
                result = "Success"

        await ctx.send(f"```py\n{result}\n```")

    @commands.command(name="import")
    @commands.is_owner()
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
