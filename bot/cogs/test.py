# import discord
from discord.ext import commands


class Test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def test(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Test(bot))
