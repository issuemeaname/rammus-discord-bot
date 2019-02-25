# import discord
from discord.ext import commands

import bot.checks


class Test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @bot.checks.is_owner()
    async def test(self, ctx):
        pass

    @commands.command(aliases=["pubtest", "publictest"], hidden=True)
    async def ptest(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Test(bot))
