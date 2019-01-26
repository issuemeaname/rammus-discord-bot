import random

from discord.ext import commands

from bot.utils import embed


class Random:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pick(self, ctx, *options):
        option = random.choice(options)

        await ctx.send(f"```\n{option}\n```")

    @commands.command()
    async def randomcase(self, ctx, *, message):
        randomcase = ""

        for char in message:
            if random.random() <= 0.50:
                randomcase += char.islower() and char.upper() or char.lower()
            else:
                randomcase += char

        await ctx.send(randomcase)

    @commands.command()
    async def roll(self, ctx, dice_sides: int = 6):
        critted = ""
        unlucky = ""

        if dice_sides <= 1:
            dice_sides = 6

        rolled = random.randint(1, dice_sides)

        if rolled == dice_sides:
            critted = "**Critical Strike!**"
        elif rolled == 1:
            unlucky = "Yikes..."

        title = f"You rolled a {dice_sides}-sided dice."
        desc = f"{critted} A {rolled} was rolled! {unlucky}"

        await ctx.send(embed=embed(title, desc))


def setup(bot):
    bot.add_cog(Random(bot))
