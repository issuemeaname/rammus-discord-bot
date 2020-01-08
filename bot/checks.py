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


def in_guild(guild_id):
    def predicate(ctx):
        """
        Check if the person invoking the command, also known as the author,
        is the member given (ID verification)
        """
        print(">>> in_guild", ctx.guild.id == guild_id)
        return ctx.guild.id == guild_id
    return commands.check(predicate)


def is_owner():
    def predicate(ctx):
        """
        Verify if author is one of the owners
        """
        return ctx.author.id in OWNERS
    return commands.check(predicate)


def mod_command():
    def predicate(ctx):
        return commands.has_permissions(administrator=True)
    return commands.check(predicate)


def is_guild_owner():
    def predicate(ctx):
        """
        Verifies if the person invoking the command is the owner of the server
        the command is used in
        """
        return ctx.author == ctx.guild.owner
    return commands.check(predicate)
