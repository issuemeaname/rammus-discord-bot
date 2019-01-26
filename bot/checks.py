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


def is_owner():
    def predicate(ctx):
        """
        Verify if author is one of the owners
        """
        return ctx.author.id in OWNERS
    return commands.check(predicate)


def delete():
    async def predicate(ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        return True
    return commands.check(predicate)
