import asyncio
import datetime

import discord
from discord.ext import commands

import bot.checks
from bot.db import Mod
from bot.resources import List
from bot.utils import create_embed


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DM = self.dm  # alias

    def get_time(self, timestamp: int):
        date_format = "`%m/%d/%Y @ %I:%M:%S %p`"
        return datetime.datetime.fromtimestamp(timestamp).strftime(date_format)

    def calculate_perms(self, author, member):
        roles = author.guild.roles

        return roles.index(author.top_role) > roles.index(member.top_role)

    async def dm(self, member: discord.Member, message, reason):
        message += reason and f" for the following: {reason}" or ""

        try:
            await member.send(message)
        except discord.errors.Forbidden:  # dm failed
            pass

    @commands.command(aliases=["admin", "mod"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def addmod(self, ctx, member: discord.Member):
        desc = f"{member.mention} is already a mod."
        guild_mods = Mod.get_mods(member.guild.id)

        if member.id not in guild_mods:
            Mod.add_mod(member)
            desc = f"Added {member.mention} to mods!"
        elif member.bot is True:
            desc = "You cannot add **bots** as moderators."

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(aliases=["unmod", "unadmin"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def delmod(self, ctx, member: discord.Member):
        desc = f"{member.mention} is not a mod."
        guild_mods = Mod.get_mods(member.guild.id)

        if member.id in guild_mods and member.guild_permissions.administrator:
            desc = "Those with admin permissions cannot be removed from mods."
        elif member.guild_permissions.administrator is False:
            Mod.del_mod(member)
            desc = f"Deleted {member.mention} from mods!"

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(aliases=["listmods", "admins"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def mods(self, ctx):
        desc = ""
        guild_mods = Mod.get_mods(ctx.guild.id)
        guild_mods = guild_mods + [m.id for m in ctx.guild.members
                                   if m.guild_permissions.administrator
                                   and m.bot is False]

        for member_id in guild_mods:
            member_found = ctx.guild.get_member(member_id)

            if member_found is None:
                Mod.del_mod(member_found)
                guild_mods.remove(member_id)

                continue
            desc += f"{member_found.mention}\n"

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        title = "Warning"
        desc = f"{member.mention} has been warned"
        message = (f"You were warned in **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        member_warnings = Mod.get_warnings(member)
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": f"{ctx.author.mention}",
            "Reason": reason,
            "Total Warnings": f"`{len(member_warnings)+1}`"
        }

        Mod.add_warn(member, ctx.author, reason)
        await ctx.send(embed=create_embed(title, desc, fields=fields))
        await self.dm(member, message, reason)

    @commands.command(aliases=["getwarns"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def warnings(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        MOD_STR = "User left"
        member_warnings = Mod.get_warnings(member)
        title = f"Warnings (**{len(member_warnings):,}**)"
        desc = ""

        if len(member_warnings) == 0:
            desc = "`None`"

        for warning in member_warnings:
            moderator_id, reason, timestamp = warning.values()
            moderator = ctx.guild.get_member(moderator_id).mention or MOD_STR
            created_at = self.get_time(timestamp)

            desc += (f"Created: {created_at}\n"
                     f"Moderator: {moderator}\n"
                     f"Reason: {reason}\n\n")

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(aliases=["clearwarn"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: discord.Member):
        Mod.clear_warns(member)

    @commands.command(aliases=["permissions"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def perms(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        perms = member.guild_permissions
        perm_values = []
        title = "Permissions"
        desc = ""

        if ctx.guild.owner.id == member.id:
            desc += ":white_check_mark: Server owner\n"
        if perms.administrator:
            desc += ":white_check_mark: Administrator\n"

        for key in List.permissions:
            name = key.replace("_", " ").title()
            has_perm = getattr(perms, key)
            box = ":x:"
            perm_values.append(has_perm)

            if has_perm:
                box = ":white_check_mark:"

            desc += f"{box} {name}\n"

        await ctx.send(embed=create_embed(title, desc, author=member))

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member.id == ctx.author.id:
            return
        message = (f"You were kicked from **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": ctx.author.display_name
        }

        if reason is not None:
            fields["Reason"] = reason

        embed = create_embed(member.display_name, f"{member.mention} was "
                                                  f"kicked", fields=fields)
        await member.kick(reason=reason)
        await ctx.send(embed=embed)
        await self.dm(member, message, reason)

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        title = member.display_name
        desc = f"{member.mention} was banned"
        has_higher_roles = self.calculate_perms(ctx.author, member)
        message = (f"You were banned from **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": ctx.author.display_name
        }

        if ctx.author.id == member.id:
            return
        if has_higher_roles is False:
            return
        if ctx.author.guild_permissions.administrator is False:
            return

        if reason is not None:
            fields["Reason"] = reason

        embed = create_embed(title, desc, fields=fields)
        await member.ban(reason=reason)
        await ctx.send(embed=embed)
        await self.dm(member, message, reason)

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        bans = await ctx.guild.bans()
        user_banned = any([user_id == ban.user.id for ban in bans])
        title = str(user_id)
        desc = f"No member with ID `{user_id}` has been banned"

        if user_banned:
            user = self.bot.get_user(user_id)
            title = user.display_name
            desc = f"{user.mention} has been unbanned!"
            await ctx.guild.unban(user)

        await ctx.send(embed=create_embed(title, desc))

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(read_message_history=True,
                                  manage_messages=True)
    async def purge(self, ctx, number: int):
        title = "Purge"
        desc = None

        if number < 0 or number > 500:
            desc = (f"`number` must be a number equal or up to `500`, not "
                    f"{number}")

            await ctx.send(embed=create_embed(title, desc))
            return
        append = number == 1 and "message" or "messages"

        try:
            await ctx.channel.purge(limit=number, before=ctx.message)
        finally:
            desc = f"Successfully purged `{number}` {append}"
            message = await ctx.send(embed=create_embed(title, desc))

            await asyncio.sleep(5)
            await message.delete()

    @commands.command(aliases=["setnick"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nick=None):
        desc = (f"**{nick}** is too short/long, it must be between 2 - 32 "
                f"characters long")

        # there may be a better way to go about this, for now this will do
        if nick is not None and (len(nick) < 2 or len(nick) > 32) is False:
            desc = (f"Successfully changed {member.mention}'s name to "
                    f"**{nick}**!")

            await member.edit(nick=nick)
        elif nick is None:
            desc = f"Successfully reset {member.mention}'s name!"

            await member.edit(nick=nick)

        await ctx.send(embed=create_embed("Nick", desc))

    @commands.command()
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, delay=15):
        title = "Slowmode has been enabled"
        desc = f"You can type a new message every `{delay}` seconds!"

        if ctx.channel.slowmode_delay == delay:
            title = f"The slowmode delay is already at {delay}s"
            desc = "There is no need to change it!"
        elif delay < 0 or delay > 120:
            scale = delay < 0 and "low" or "high"
            title = f"The delay is too {scale}"
            desc = "It must be from 0 - 120!"
        elif delay == 0:
            title = "Slowmode has been disabled"
            desc = "You may now type freely."

        await ctx.channel.edit(slowmode_delay=delay)
        await ctx.send(embed=create_embed(title, desc))


def setup(bot):
    bot.add_cog(Moderation(bot))
