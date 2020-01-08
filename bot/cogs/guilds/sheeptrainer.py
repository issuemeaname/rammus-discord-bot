# import discord
from discord.ext import commands

import bot.checks


class Sheeptrainer(commands.Cog, command_attrs={"hidden": True}):
    _GUILD = 296463400064647168

    def __init__(self, bot):
        self.bot = bot

    @bot.checks.in_guild(_GUILD)
    async def cog_check(self, ctx):
        print("a")
        return True

    @commands.command(usage="{0}part 8")
    async def part(self, ctx, number: int = None):
        if number == 8:
            await ctx.send("Have ur balls removed")


def setup(bot):
    bot.add_cog(Sheeptrainer(bot))
