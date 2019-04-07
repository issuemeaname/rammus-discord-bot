# import discord
from discord.ext import commands

import bot.checks


class GuildSpecific(commands.Cog, name="Guild-Specific"):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {
            "Sheeptrainer": 296463400064647168
        }

    # sheeptrainer's
    @commands.command(usage="{0}part 8", hidden=True)
    @bot.checks.in_guild(296463400064647168)
    async def part(self, ctx, number: int = None):
        if number == 8:
            await ctx.send("Have ur balls removed")


def setup(bot):
    bot.add_cog(GuildSpecific(bot))
