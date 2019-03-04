import discord
from discord.ext import commands

from bot.resources import OWNERS


def delete():
    async def predicate(ctx):
        await ctx.message.delete()

        return True
    return commands.check(predicate)


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
    return commands.check(predicate)


def both_have_perms(**kwargs):
    def predicate(ctx):
        ctx.author.permissions_in(ctx.channel) \
           and commands.bot_has_permissions(**kwargs)
    return commands.check(predicate)


def mod_command():
    def predicate(_):
        return commands.has_permissions(administrator=True)
    return commands.check(predicate)
