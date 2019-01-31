import random

import discord
from discord.ext import commands

import bot.checks
from bot.resources import List
from bot.utils import embed


class Fun:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @bot.checks.delete()
    async def say(self, ctx, *, message):
        await ctx.send(message)

    @commands.command()
    async def iq(self, ctx, member: discord.Member = None):
        mention = member and member.mention or ctx.author.mention
        iq = random.randint(-263, 263)

        await ctx.send(f"{mention} {iq}")

    @commands.command()
    async def bigtext(self, ctx, *, message):
        bigtext = ""
        append = " "

        for i, char in enumerate(message):
            char = char.lower()

            if i+1 == len(message):
                append = ""

            if char.isdigit():
                char = List.digits[char]
            elif char.isalpha():
                char = f":regional_indicator_{char}:"
            elif char == " ":
                char = char*2
            else:
                char = ""

            bigtext += char + append

        await ctx.send(bigtext)

    @commands.command()
    async def cringe(self, ctx):
        await ctx.send(random.choice(List.cringe))

    @commands.command()
    async def hug(self, ctx, member: discord.Member):
        file = random.choice(List.hugs)
        embed_ = embed(desc=f":hugging: {ctx.author.mention} hugged "
                            f"{member.mention}!", image=file)

        await ctx.send(embed=embed_, file=file)


def setup(bot):
    bot.add_cog(Fun(bot))
