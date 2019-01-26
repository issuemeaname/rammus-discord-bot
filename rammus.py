import asyncio
import datetime
import time
from collections import namedtuple

import discord
from discord.ext import commands

from bot.resources import OWNERS
from bot.resources import PREFIX
from bot.resources import Path
from bot.token import TOKEN
from bot.utils import clear_screen
from bot.utils import embed
from bot.utils import get_tb_message


class Rammus(commands.Bot):
    # magic methods
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(PREFIX))
        self.file = __file__
        self.init_time = int(time.time())
        self.remove_command("help")
        self.setup(pre_clear=True)

    async def on_minute(self):
        while True:
            current_time = int(time.time())
            uptime = datetime.timedelta(seconds=current_time - self.init_time)
            print(current_time, self.init_time, uptime, sep="\n")
            activity = discord.Game(f"WIP | {uptime}s uptime")

            await self.change_presence(activity=activity)
            await asyncio.sleep(60)

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
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def before_invoke(self, ctx):
        pass

    async def on_connect(self):
        self.app_info = await self.application_info()
        self.owner = self.app_info.owner
        self.owners = OWNERS

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
        clear_screen("windows", post_message=f"{self.user.name}\n")
        await self.log(embed=embed("Status", "Online"), log=self.logs.status)


bot = Rammus()

if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)
