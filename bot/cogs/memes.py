# import discord
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["nword"])
    async def n(self, ctx):
        await ctx.send(f"**{ctx.author.display_name}** is going to say the N "
                       f"word.")


def setup(bot):
    bot.add_cog(Memes(bot))
