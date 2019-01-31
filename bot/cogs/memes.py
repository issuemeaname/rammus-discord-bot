# import discord
# from discord.ext import commands


class Memes:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Memes(bot))
