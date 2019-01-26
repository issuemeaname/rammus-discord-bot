import discord

from discord.ext import commands


class ErrorHandler:
    def __init__(self, bot):
        self.bot = bot
        self.ignored_errors = [
            discord.errors.NotFound,
            commands.errors.CommandNotFound,
            commands.errors.CheckFailure
        ]

    def is_ignored(self, error):
        # ierror: ignored error
        return any([isinstance(error, ie) for ie in self.ignored_errors])

    async def on_command_error(self, ctx, error):
        message = ctx.message.content
        print(type(error).__name__, isinstance(error, discord.errors.NotFound),
              isinstance(error, discord.NotFound))
        print(type(error).__name__,
              isinstance(error, discord.errors.Forbidden),
              isinstance(error, discord.errors.Forbidden))

        if self.is_ignored(error):
            return

        if isinstance(error, commands.errors.CommandInvokeError):
            await self.bot.log(message, error=error.original)
        elif isinstance(error, discord.errors.Forbidden):
            await ctx.author.send(f"You must use `>{ctx.command.name}` in a "
                                  f"server that both of us are in!")
        else:
            await self.bot.log(message, error=error)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
