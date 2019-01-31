# import discord
from discord.ext import commands


class TextManipulation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def split(self, ctx, *, message):
        await ctx.send((" ").join(message))


def setup(bot):
    bot.add_cog(TextManipulation(bot))
