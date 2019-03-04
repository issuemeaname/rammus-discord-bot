import discord
from discord.ext import commands

from bot.utils import create_embed


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_errors = [
            discord.errors.NotFound,
            commands.errors.CommandNotFound,
            commands.errors.CheckFailure
        ]

    def is_ignored(self, error):
        # ierror: ignored error
        return any([type(error) is ie for ie in self.ignored_errors])

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        message = ctx.message.content
        title = None
        desc = None
        embed = None

        if type(error) is commands.errors.CommandInvokeError:
            error = error.original
        if self.is_ignored(error):
            return

        if isinstance(error, (commands.errors.MissingPermissions,
                              discord.errors.Forbidden)):
            title = "Error"
            desc = f"`>{ctx.command}` failed due to insufficient permissions."
        else:
            await self.bot.log(message, error=error)

        if None not in [title, desc]:
            embed = create_embed(title, desc)

        if embed is not None:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
