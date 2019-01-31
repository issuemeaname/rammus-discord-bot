import discord
from discord.ext import commands

from bot.resources import OWNERS


def is_member(*members):
    def predicate(ctx):
        """
        Check if the person invoking the command, also known as the author,
        is the member given (ID verification)
        """
        return ctx.author.id in members
    return commands.check(predicate)


def in_guild(*guilds):
    def predicate(ctx):
        """
        Check if the person invoking the command, also known as the author,
        is the member given (ID verification)
        """
        return ctx.guild.id in guilds
    return commands.check(predicate)


def is_owner():
    def predicate(ctx):
        """
        Verify if author is one of the owners
        """
        return ctx.author.id in OWNERS
    passed = commands.check(predicate)

    if passed:
        return passed
    # raise commands.errors.NotOwner()


def delete():
    async def predicate(ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        return True
    return commands.check(predicate)
