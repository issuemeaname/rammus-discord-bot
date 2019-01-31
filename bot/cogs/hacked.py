# import discord
from discord.ext import commands

import bot.checks


class Hacked:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True)
    @bot.checks.is_owner()
    @bot.checks.delete()
    async def hacked(self, ctx):
        pass

    @hacked.command()
    async def iq(self, ctx):
        await ctx.send(f"{ctx.author.mention} **Basically fucking infinity "
                       f"at this point.**")


def setup(bot):
    bot.add_cog(Hacked(bot))
