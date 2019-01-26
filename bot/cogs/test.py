# import discord
from discord.ext import commands

from bot.utils import wrap


class Test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def test(self, ctx):
        message = ("\n").join([p[0].replace("_", " ").title() + f" = {p[1]}" for p in ctx.author.guild_permissions])

        for block in wrap(message):
            await ctx.send(block)


def setup(bot):
    bot.add_cog(Test(bot))
