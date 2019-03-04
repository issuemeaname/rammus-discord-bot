import discord
from discord.ext import commands

import bot.checks
from bot.utils import wrap


class GuildSpecific(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # sheeptrainer's
    @commands.command(hidden=True)
    @bot.checks.in_guild(296463400064647168)
    async def part(self, ctx, number: int = None):
        if number == 8:
            await ctx.send("Have ur balls removed")

    # league of fuckers
    @commands.group(hidden=True)
    @bot.checks.in_guild(545546049461288970)
    async def role(self, ctx):
        if ctx.command.invoked_subcommand is None:
            await ctx.send("sub command")

    @role.command()
    async def get(self, ctx, *, name: discord.Role):
        role = discord.utils.get(ctx.guild.roles, name=name)

        if role is None:
            await ctx.send("This role doesn't exist, you can create it using "
                           "`>role create` and then the role's name that you "
                           "want.")

    @role.command(aliases=["color"])
    async def colour(self, ctx, r: int = None, g: int = None, b: int = None):
        b = r == g == b == 0 and 1 or bot
        r = g = b = r is g is b is None and 0
        author_role = [role for role in ctx.author.roles
                       if role.name != "@everyone"][0]

        await author_role.edit(colour=discord.Colour(""))

    @role.command()
    async def list(self, ctx):
        roles = [role.name for role in ctx.guild.roles
                 if role.name not in ["@everyone", "Rammus"]]
        message = ("\n").join(roles)

        for block in wrap(message):
            await ctx.send(block)


def setup(bot):
    bot.add_cog(GuildSpecific(bot))
