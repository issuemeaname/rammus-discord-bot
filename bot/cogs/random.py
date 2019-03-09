import random
from typing import Union

import discord
from discord.ext import commands

from bot.resources import List
from bot.resources import Colours
from bot.utils import create_embed


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pick(self, ctx, *options):
        option = random.choice(options)

        await ctx.send(f"```\n{option}\n```")

    @commands.command()
    async def randomcase(self, ctx, *, message):
        randomcase = ""
        file = None

        if message.endswith(" --image"):
            message = message.replace(" --image", "")
            file = discord.File(r"bot\images\randomcase\image.jpg")

        for char in message:
            if random.random() <= 0.50:
                randomcase += char.islower() and char.upper() or char.lower()
            else:
                randomcase += char

        await ctx.send(randomcase, file=file)

    @commands.command()
    async def roll(self, ctx, dice_sides: Union[int, float] = 6):
        critted = ""
        unlucky = ""

        if type(dice_sides) is float:
            dice_sides = int(dice_sides)
        if dice_sides <= 1:
            dice_sides = 6

        rolled = random.randint(1, dice_sides)

        if rolled == dice_sides:
            critted = "**Critical Strike!**"
        elif rolled == 1:
            unlucky = "Yikes..."

        title = f"You rolled a {dice_sides:,}-sided dice."
        desc = f"{critted} A {rolled:,} was rolled! {unlucky}"

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question):
        if question.endswith("?") is False:
            question += "?"
        responses = List.responses_8ball
        response_type = random.choice(list(responses.keys()))
        colour = (response_type == "Positive" and Colours.GREEN or
                  response_type == "Vague" and Colours.ORANGE or Colours.RED)
        response = random.choice(responses.get(response_type).values())
        fields = {
            "Question": question,
            "Type": response_type,
            "Response": response
        }

        embed = create_embed(title="8ball", colour=colour, fields=fields)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Random(bot))
