import discord
from discord.ext import commands

from bot.utils import send_with_embed


class ErrorHandler(commands.Cog, name="Error Handler"):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_errors = [
            commands.CheckFailure,
            commands.CommandNotFound,
            commands.NotOwner,
            discord.Forbidden,
            discord.NotFound
        ]

    def is_ignored(self, error):
        # ie = Ignored Error
        return any([type(error) is ie for ie in self.ignored_errors])

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        title = desc = ""
        fields = {}

        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if self.is_ignored(error):
            return

        if isinstance(error, (commands.MissingRequiredArgument)):
            title = f"Missing argument for `{ctx.invoked_with}`"
            desc = f"`{error.param.name.title()}`"
        elif isinstance(error, (commands.MissingPermissions,
                                discord.Forbidden)):
            title = "Error"
            desc = (f"`{ctx.command.name.title()}` failed due to insufficient "
                    f"permissions.")
            fields = {
                "Missing Permissions": error.missing_perms
            }
        elif isinstance(error, (commands.BadArgument,
                                commands.BadUnionArgument)):
            help_command = self.bot.get_command("help")

            return await ctx.invoke(help_command, ctx.command.name)
        else:
            return await self.bot.log(ctx.message.content, error=error)
        return await send_with_embed(ctx, title, desc, fields=fields)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
