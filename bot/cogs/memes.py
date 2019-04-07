from typing import Union

import discord
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="{0}f chat\n{0}f @DJ#3333", aliases=["respect"])
    async def f(self, ctx, *, reason: Union[discord.Member, str] = None):
        """
        Pay your respects to anything whether it's a member or a specific
        reason
        """
        append = ":cry:"

        if type(reason) is discord.Member:
            append = f"for **{reason.display_name}** {append}"
        elif type(reason) is str:
            append = f"for **{reason}** {append}"

        await ctx.send(f"**{ctx.author.display_name}** has paid their "
                       f"respects {append}")

    @commands.command(usage="{0}n", aliases=["nword"])
    async def n(self, ctx):
        """
        Exert your dominance by announcing that you are going to say the
        dreaded "N word"
        """
        await ctx.send(f"**{ctx.author.display_name}** is going to say the N "
                       f"word.")

    @commands.command(name="pass")
    async def _pass(self, ctx, member: discord.Member):
        """
        Give your best homie the N word pass
        """
        await ctx.send(f"{member.mention} Here is your N word pass.\n\n"

                       f"Signed,\n"
                       f"**{ctx.author.display_name}**")


def setup(bot):
    bot.add_cog(Memes(bot))
