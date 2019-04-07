import random

import discord
from discord.ext import commands

import bot.checks
from bot.resources import List
from bot.utils import create_embed


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="{0}say Hello World")
    @bot.checks.delete()
    async def say(self, ctx, *, message):
        """
        Sends the given message as Rammus
        """
        await ctx.send(message)

    @commands.command(usage="{0}id\n{0}id @DJ#3333")
    async def iq(self, ctx, member: discord.Member = None):
        """
        Show the IQ of either yourself or the given person
        """
        mention = member and member.mention or ctx.author.mention
        iq = random.randint(-263, 263)

        await ctx.send(f"{mention} {iq}")

    @commands.command(usage="{0}hug")
    async def hug(self, ctx, member: discord.Member):
        """
        Send some feel good energy by hugging someone
        """
        desc = f":hugging: {ctx.author.mention} hugged {member.mention}!"
        file = random.choice(List.hugs)
        embed = create_embed(desc=desc, image=file)

        await ctx.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(Fun(bot))
