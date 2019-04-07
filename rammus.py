import asyncio
import datetime
import random
import time
from collections import namedtuple

import discord
from discord.ext import commands

from bot.db import Guilds
from bot.resources import command_prefix
from bot.resources import List
from bot.resources import OWNERS
from bot.resources import Path
from bot.token import TOKEN
from bot.utils import clear_screen
from bot.utils import create_embed
from bot.utils import get_tb_message


class Rammus(commands.Bot):
    # magic methods
    def __init__(self):
        super().__init__(command_prefix=command_prefix)
        self.file = __file__
        self.remove_command("help")
        self.setup(pre_clear=True)

    async def on_minute(self):
        self.init_time = int(time.time())
        passed = 0

        while True:
            uptime = datetime.timedelta(seconds=self.init_time - passed)
            status = random.choice(List.statuses)
            activity = discord.Game(f"{status} | {uptime}s uptime")

            await self.change_presence(activity=activity)
            await asyncio.sleep(60)

            passed += 60

    # standard methods
    def setup(self, pre_clear=False):
        if pre_clear:
            clear_screen("windows")

        for cog in Path.cogs:
            self.load_extension(cog)

            print("Loaded", cog)

    async def log(self, message=None, cause=None, log=None, error=None,
                  embed=None):
        log = log or self.logs.default

        if error:
            log = self.logs.error
            message = f"```py\n{message}\n\n{get_tb_message(error)}\n```"

        if cause and embed:
            embed.add_field(name="Cause", value=f"`{cause}`")

        await log.send(message, embed=embed)

    # discord event methods
    async def on_connect(self):
        self.app_info = await self.application_info()
        self.owner = self.app_info.owner
        self.owners = OWNERS

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print("Join")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print("Remove")

    async def on_ready(self):
        Logs = namedtuple("Logs", ["default", "status", "error"])
        self.init_time = int(time.time())
        self.guild = self.get_guild(464446709146320897)
        self.logs = Logs(default=self.get_channel(530005984891109386),
                         status=self.get_channel(464446775135174656),
                         error=self.get_channel(530001923399483413))

        # setup loops
        self.loop.create_task(self.on_minute())

        # visuals
        clear_screen("windows", message=f"{self.user.name}\n")
        await self.log(embed=create_embed(title="Status", desc="Online"),
                       log=self.logs.status)


bot = Rammus()


@bot.check
async def pre_command(ctx):
    if ctx.guild is not None:
        return ctx.guild.me.permissions_in(ctx.channel).send_messages

    await ctx.send(f"You must use `>{ctx.command.name}` in "
                   f"a server that both you and Rammus are "
                   f"in!")
    return False

if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)
