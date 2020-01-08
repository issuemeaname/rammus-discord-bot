import datetime
import os
import random
import signal
import time
from collections import namedtuple

import discord
from discord.ext import commands
from discord.ext import tasks

from bot.db import save_all_dbs
from bot.resources import BLACKLIST
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
        self.seconds = 0
        self.ready = False
        self.remove_command("help")

        self.Log = namedtuple("Logs", ["default", "status", "error"])
        clear_screen("windows", message="Rammus\n")
        print("Connecting...")

    # standard methods
    def setup(self):
        for cog in Path.cogs:
            self.load_extension(cog)

            print(f"Loading {cog}")

    async def get_self(self, ctx):
        return await ctx.guild.fetch_member(self.user.id)

    async def log(self, message=None, cause=None, log=None, error=None,
                  embed=None):
        log = log is not None and log or self.logs.default

        if error:
            log = self.logs.error
            message = (f"```py\n"
                       f"{message}\n\n"

                       f"{get_tb_message(error)}\n"
                       f"```")

        if cause and embed:
            embed.add_field(name="Cause", value=f"`{cause}`")

        await log.send(message, embed=embed)

    # background tasks
    @tasks.loop(minutes=1.0)
    async def on_minute(self):
        uptime = datetime.timedelta(seconds=self.seconds)
        status = random.choice(List.statuses)
        activity = discord.Game(f"{status} | {uptime}s uptime")
        self.seconds += 60

        await self.change_presence(activity=activity)

    # discord.py core methods
    async def close(self, ctx):
        await save_all_dbs()

        if ctx.command.name == "close":
            os.kill(os.getppid(), signal.SIGTERM)
        await super().close()

    # discord.py event methods
    async def on_connect(self):
        self.app_info = await self.application_info()
        self.owner = self.app_info.owner
        self.owners = OWNERS

        print("Connection established...")

    async def on_message(self, message):
        if message.author.id in BLACKLIST:
            return True

        self.process_commands(message)

    async def on_ready(self):
        # debounce
        if self.ready:
            return self.ready

        self.ready = True

        # setup
        #   offline
        print("Setting up...")
        self.setup()

        #   online
        self.init_time = int(time.time())
        self.guild = self.get_guild(464446709146320897)
        self.logs = self.Log(default=self.get_channel(530005984891109386),
                             status=self.get_channel(464446775135174656),
                             error=self.get_channel(530001923399483413))

        # background tasks
        self.on_minute.start()

        # uptime report
        print("Setup complete...")
        await self.log(embed=create_embed(title="Status", desc="Online"),
                       log=self.logs.status)
        print("Running...")


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
    try:
        bot.loop.run_until_complete(bot.start(TOKEN, reconnect=True))
    except Exception:
        bot.loop.run_until_complete(bot.close())
