import asyncio
import datetime
from typing import Union

import discord
from discord.ext import commands

import bot.checks
from bot.db import Guilds
from bot.prefix import DEFAULT
from bot.resources import List
from bot.utils import create_embed
from bot.utils import wrap


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

    async def send_message(self, member, join=False, leave=False):
        channel = Guilds.get_channel(member.guild.id)
        message = Guilds.get_message(member.guild.id, join=join, leave=leave)

        # if system channel and message exists, format then send message
        # using system channel
        if None not in [channel, message]:
            channel = member.guild.get_channel(channel)

            if channel is not None:
                for hotstring, attr in Guilds.message_features.items():
                    sub = member

                    if attr is not None:
                        for name in attr.split("."):
                            sub = getattr(sub, name)

                    message = message.replace(hotstring, str(sub))

                await channel.send(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        roles = Guilds.get_roles(member.guild.id).get("join")

        if roles not in [list(), None] and member.bot is False:
            roles = [member.guild.get_role(r) for r in roles]

            await member.add_roles(*roles)

        await self.send_message(member, join=True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_message(member, leave=True)

    async def dm(self, member: discord.Member, message, reason):
        message += reason and f" for the following: {reason}" or ""

        try:
            await member.send(message)
        except discord.errors.Forbidden:  # dm failed
            pass

    @commands.command(usage="{0}addmod @DJ#3333", aliases=["admin", "mod"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def addmod(self, ctx, member: discord.Member):
        """
        Add a moderator to the list of server moderators
        """
        desc = f"{member.mention} is already a mod."
        guild_mods = Guilds.get_mods(member.guild.id)

        if member.id not in guild_mods:
            Guilds.add_mod(member)
            desc = f"Added {member.mention} to mods!"
        elif member.bot is True:
            desc = "You cannot add **bots** as moderators."

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(usage="{0}delmod @DJ#3333", aliases=["unmod", "unadmin"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def delmod(self, ctx, member: discord.Member):
        """
        Remove a moderator from the server
        """
        desc = f"{member.mention} is not a mod."
        guild_mods = Guilds.get_mods(member.guild.id)

        if member.id in guild_mods and member.guild_permissions.administrator:
            desc = "Those with admin permissions cannot be removed from mods."
        elif member.guild_permissions.administrator is False:
            Guilds.del_mod(member)
            desc = f"Deleted {member.mention} from mods!"

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(usage="{0}mods", aliases=["listmods", "admins", "m"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def mods(self, ctx):
        """
        Displays all of the mods within a server

        **Note**: this also shows the server owner and those with the
        administrator permission
        """
        desc = ""
        guild_mods = Guilds.get_mods(ctx.guild.id)
        guild_mods = guild_mods + [m.id for m in ctx.guild.members
                                   if m.guild_permissions.administrator
                                   and m.bot is False]

        for member_id in guild_mods:
            member_found = ctx.guild.get_member(member_id)

            if member_found is None:
                Guilds.del_mod(member_found)
                guild_mods.remove(member_id)

                continue
            desc += f"{member_found.mention}\n"

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(usage="{0}warn @DJ#3333 chat filter bypass",
                      aliases=["w"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        """
        Warn a member for the specified reason
        """
        title = "Warning"
        desc = f"{member.mention} has been warned"
        message = (f"You were warned in **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        member_warnings = Guilds.get_warnings(member)
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": f"{ctx.author.mention}",
            "Reason": reason,
            "Total Warnings": f"`{len(member_warnings)+1}`"
        }

        Guilds.add_warn(member, ctx.author, reason)
        await ctx.send(embed=create_embed(title, desc, fields=fields))
        await self.dm(member, message, reason)

    @commands.command(usage="{0}warnings\n{0}warnings @DJ#3333",
                      aliases=["warns", "getwarns"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def warnings(self, ctx, member: discord.Member = None):
        """
        Displays the warnings for the given member in the server this command
        is used in
        """
        member = member or ctx.author
        no_mod = "User left"
        member_warnings = Guilds.get_warnings(member)
        title = f"Warnings (**{len(member_warnings):,}**)"
        desc = ""

        if len(member_warnings) == 0:
            desc = "`None`"

        for warning in member_warnings:
            moderator_id, reason, timestamp = warning.values()
            moderator = ctx.guild.get_member(moderator_id).mention or no_mod
            created_at = self.get_time(timestamp)

            desc += (f"Created: {created_at}\n"
                     f"Moderator: {moderator}\n"
                     f"Reason: {reason}\n\n")

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}clearwarns @DJ#3333", aliases=["clearwarn"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: discord.Member):
        """
        Remove all of the warnings for the given member in the server
        this command is used in
        """
        warnings, _ = Guilds.clear_warns(member)
        append = warnings == 1 and "warn" or "warns"
        desc = f"Cleared {warnings} {append}"

        embed = create_embed(title="Clearwarns", desc=desc)
        await ctx.send(embed=embed)

    @commands.command(usage="{0}perms\n{0}perms @DJ#3333",
                      aliases=["permissions"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def perms(self, ctx, member: discord.Member = None):
        """
        Show the permissions given to the specified member

        Note: if the member has the special "administrator" permission or is
        the owner of the server this command is used in, these permissions
        will be shown and by default every permission will be granted.
        """
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

    @commands.command(usage="{0}kick @DJ#3333\n{0}kick @DJ#3333 3 warnings",
                      aliases=["k"])
    @bot.checks.delete()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kicks the given member from the guild - if a reason is specified, this
        will be displayed in the audit logs
        """
        title = member.display_name
        desc = f"{member.mention} was kicked"
        kickable = True
        message = (f"You were kicked from **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": ctx.author.display_name
        }

        if member.id == ctx.author.id:
            kickable = False
            fields = None
            desc = "You **cannot** kick yourself!"

        if reason is not None:
            fields["Reason"] = reason

        embed = create_embed(title, desc, fields=fields)
        if kickable:
            await member.kick(reason=reason)
            await self.dm(member, message, reason)

        await ctx.send(embed=embed)

    @commands.command(usage="{0}ban @DJ#3333\n{0}ban @DJ#3333 raiding",
                      aliases=["b"])
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: Union[discord.Member, discord.User], *,
                  reason=None):
        """
        Bans the given member or member ID from the server - if a reason is
        given, this will be displayed in the audit logs
        """
        title = member.display_name
        desc = f"{member.mention} was banned"
        bannable = True
        message = (f"You were banned from **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": ctx.author.display_name
        }

        if reason is not None:
            fields["Reason"] = reason

        if type(member) is discord.User:
            await ctx.guild.ban(member, reason=reason)
            await self.dm(member, message, reason)
            bannable = False
        elif ctx.author.id == member.id:
            desc = "You **cannot** ban yourself!"
            bannable = False
        elif self.calculate_perms(ctx.author, member) is False:
            desc = "You **cannot** ban someone who has a higher role than you!"
            bannable = False
        elif ctx.author.guild_permissions.administrator is False:
            desc = ("You **cannot** ban someone if you do not have the "
                    "administrator permission!")
            bannable = False

        if bannable:
            fields = None
            await member.ban(reason=reason)
            await self.dm(member, message, reason)

        embed = create_embed(title, desc, fields=fields)
        await ctx.send(embed=embed)

    @commands.command(usage="{0}bans")
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def bans(self, ctx):
        """
        List the members that have been banned with the given reason
        associated with their ban (if any) within the server this command is
        used in
        """
        message = ""
        bans = await ctx.guild.bans()

        if len(bans) == 0:
            message = "None"
        else:
            for entry in bans:
                reason = entry.reason or "not specified"
                message += (f"**{entry.user} ({entry.user.id})**\n"
                            f"Reason: {reason}\n")

        for desc in wrap(message, embed=True, no_blocks=True):
            await ctx.send(embed=create_embed(title="Bans", desc=desc))

    @commands.command(usage="{0}unban 173225726139564032", aliases=["u"])
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """
        Unbans the user by the given user ID
        """
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

    @commands.command(usage="{0}purge 500")
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(read_message_history=True,
                                  manage_messages=True)
    async def purge(self, ctx, number: int):
        """
        Deletes messages in bulk with a maximum of 500 message to delete at a
        time
        """
        title = "Purge"
        desc = None
        fields = None

        if number < 0 or number > 500:
            desc = (f"`number` must be a number equal or up to `500`, not "
                    f"{number}")

            await ctx.send(embed=create_embed(title, desc))
        else:
            messages = number == 1 and "message" or "messages"

            try:
                await ctx.channel.purge(limit=number, before=ctx.message)
            finally:
                desc = f"Successfully purged `{number}` {messages}"
                fields = {
                    "Note": (f"`This message will be deleted automatically in "
                             f"8s.`")
                }
                embed = create_embed(title, desc, fields=fields)
                message = await ctx.send(embed=embed)

                await asyncio.sleep(8)
                await message.delete()

    @commands.command(usage="{0}setprefix\n{0}setprefix !")
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, *, prefix=None):
        """
        Set the prefix to use for Rammus in the server, give no prefix for it
        to be reset back to the default prefix (`>`)

        Note: as of now the character limit for the prefix is 2^5 but this
        may change in the somewhat near future.
        """
        title = f"Prefix"
        desc = f"Set **{ctx.guild.name}**'s prefix to `{prefix}`"
        limit = 2**5
        guild_prefix = Guilds.get_prefix(ctx.guild.id)

        if prefix is None:
            # im sure theres a better way to do this...
            prefix = DEFAULT
            desc = f"Reset prefix to `{prefix}` for **{ctx.guild.name}**!"
            Guilds.set_prefix(ctx.guild.id, prefix)
        elif len(prefix) > limit:
            desc = (f"`{prefix}` is too long to be a valid prefix. Please use "
                    f"a prefix that is less than or equal to {limit} "
                    f"characters.")
        elif guild_prefix == prefix:
            desc = (f"`{prefix}` is already the prefix for "
                    f"**{ctx.guild.name}**!")
        else:
            Guilds.set_prefix(ctx.guild.id, prefix)

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}nick @DJ#3333\n{0}nick @DJ#3333 big loser",
                      aliases=["setnick"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nick=None):
        """
        Set the nickname of the given member to the given nickname

        Note: the nickname must be between 2 - 32 characters long, any
        nicknames shorter/longer than this will not work.
        """
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

    @commands.command(usage="{0}slowmode 15\n{0}slowmode")
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, delay: int = 15):
        """
        Toggle and control slowmode for the channel this command is used in
        """
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
        else:
            await ctx.channel.edit(slowmode_delay=delay)

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}channel #bot-logs")
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        """
        Set up a channel for member join/leave messages to be sent in
        """
        title = "Join/Leave Channel"
        action = channel is None and "Removed" or "Set"
        desc = (f"{action} join/leave channel")
        channel = channel is not None and channel.id or channel

        Guilds.set_channel(ctx.guild.id, channel)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}joinmsg\n{0}joinmsg Welcome!",
                      aliases=["joinmessage"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def joinmsg(self, ctx, *, message=None):
        """
        Set up a message to be sent whenever a member joins your server
        """
        title = "Join Message"
        action = message is None and "Removed" or "Set"
        desc = f"{action} join message"

        Guilds.set_message(ctx.guild.id, message, join=True)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}leavemsg\n{0}leavemsg Goodbye!",
                      aliases=["leavemessage"])
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def leavemsg(self, ctx, *, message=None):
        """
        Set up a message to be sent whenever a member leaves your server
        """
        title = "Leave Message"
        action = message is None and "Removed" or "Set"
        desc = f"{action} leave message"

        Guilds.set_message(ctx.guild.id, message, leave=True)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}joinrole Subscribers\n"
                            "{0}joinrole \"Join Role\" Subscribers Community",
                      aliases=["autorole"])
    @commands.has_permissions(administrator=True)
    async def joinrole(self, ctx, *roles: commands.Greedy[discord.Role]):
        """
        Set the given role to be given when a member joins

        Note: You can give multiple roles and this also works without having
        to mention the roles as well, you can type the names of the
        roles and any with spaces in them must be surrounded in quotation
        marks, e.g. ("Join Role With Spaces")
        """
        title = "Join Role" + (len(roles) == 1 and "" or "s")
        action = len(roles) == 0 and "Removed" or "Set"
        desc = f"{action} {title.lower()}"

        Guilds.set_join_roles(ctx.guild.id, roles)
        await ctx.send(embed=create_embed(title, desc))


def setup(bot):
    bot.add_cog(Moderation(bot))
