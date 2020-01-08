# import asyncio
# import discord
from discord.ext import commands

import bot.checks

# from bot.utils import send_with_embed


class Test(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @bot.checks.is_owner()
    async def test(self, ctx):
        pass

    @commands.command(aliases=["pubtest", "publictest"])
    async def ptest(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Test(bot))
