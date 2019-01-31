import asyncio

import discord
from discord.ext import commands

import bot.checks
from bot.utils import embed


class Moderation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, delay=15):
        title = "Slowmode has been disabled"
        desc = "You can now type freely."

        if ctx.channel.slowmode_delay == delay:
            title = f"The slowmode delay is at {delay}s."
            desc = "There is no need to change it!"
        elif delay < 0 or delay > 120:
            scale = delay < 0 and "low" or "high"
            title = f"The delay is too {scale}!"
            desc = "It must be from 0 - 120"
        elif delay == 0:
            title = "Slowmode has been delayed."
            desc = "You may now type freely"
        else:
            title = "The slowmode delay has been set."
            desc = f"You can type a new message every `{delay}` seconds!"

            await ctx.channel.edit(slowmode_delay=delay)

        await ctx.send(embed=embed(title, desc))

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, delay=None, *,
                  reason=None):
        # if member.id == ctx.author.id:
        #     return

        await member.ban(reason=reason)
        await member.unban()

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(read_message_history=True,
                                  manage_messages=True)
    async def purge(self, ctx, number: int):
        if number < 0 or number > 500:
            return

        messages = number == 1 and "message" or "messages"

        try:
            await ctx.channel.purge(limit=number, before=ctx.message)
        finally:
            message = await ctx.send(f"Successfully purged `{number}` "
                                     f"{messages}")

            await asyncio.sleep(5)
            await message.delete()


def setup(bot):
    bot.add_cog(Moderation(bot))
