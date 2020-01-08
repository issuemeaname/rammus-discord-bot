import datetime
import re
from typing import Optional
from typing import Union

import asyncio
import discord
from discord.ext import commands
from discord.ext import tasks

import bot.checks
from bot.db import Guilds
from bot.resources import List
from bot.utils import create_embed
from bot.utils import wrap

EMPTY_LIST = []


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DM = self.dm  # alias
        self.mutes = {}

    def get_time(self, timestamp: int):
        date_format = "`%m/%d/%Y @ %I:%M:%S %p`"
        return datetime.datetime.fromtimestamp(timestamp).strftime(date_format)

    def calculate_perms(self, author,
                        obj: Union[discord.Member, discord.Role]):
        bot = author.guild.me
        obj = type(obj) is discord.Member and obj.top_role or obj

        return (author.guild.owner == author or
                author.top_role.position > obj.position and
                bot.top_role.position > obj.position)

    def resolve_delay(self, delay_str):
        regex = re.compile(r"(\d+)([smh])")
        match_found = regex.search(delay_str)
        multipliers = list("smh")

        if match_found:
            time, multiplier = match_found.groups()
            time = int(time) * 60 ** multipliers.index(multiplier.lower())

            return time

    def get_mute_role(self, guild):
        return discord.utils.get(guild.roles, name="Muted") or None

    async def setup_mute_role(self, guild):
        colour = discord.Colour.teal()
        permissions = discord.Permissions()
        permissions.update(read_message_history=True)
        mute_role = await guild.create_role(name="Muted", colour=colour,
                                            permissions=permissions)

        for channel in guild.channels:
            permissions = {}

            if type(channel) in [discord.TextChannel,
                                 discord.CategoryChannel]:
                permissions = {
                    "send_messages": False,
                    "add_reactions": False
                }
            elif type(channel) is discord.VoiceChannel:
                permissions = {
                    "speak": False
                }

            await channel.set_permissions(mute_role, **permissions)
        return mute_role

    async def send_message(self, member, mtype):
        channel = await Guilds.get_channel(member.guild.id)
        message = await Guilds.get_message(member.guild.id, mtype)

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

    async def dm(self, member: discord.Member, message, reason):
        message += reason and f" for the following: {reason}" or ""

        try:
            return await member.send(message)
        except discord.Forbidden:
            return False

    @tasks.loop(seconds=1.0)
    async def on_second(self, ctx, member):
        member_data = self.mutes.get(member.id)
        member.data["time"] -= 1

        if member_data.get("time") == 0:
            title = "Mute"
            desc = f"Unmuted **{member}**"
            task = member_data.get("task")
            mute_role = (self.get_mute_role(ctx.guild) or
                         await self.setup_mute_role(ctx.guild))

            await member.remove_roles(mute_role)
            await member.edit(mute=False)
            await ctx.send(embed=create_embed(title, desc))
            task.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 350248744773615626:
            difference = datetime.datetime.now() - member.created_at

            if difference.days < 1:
                return await member.ban(reason="Vitamin D xo")

        guild_roles = await Guilds.get_roles(member.guild.id)
        join_roles = guild_roles.get("join")

        if join_roles not in [list(), None] and member.bot is False:
            roles = [member.guild.get_role(r) for r in join_roles]

            await member.add_roles(*roles)

        await self.send_message(member, "join")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_message(member, "leave")

    @commands.Cog.listener()
    @commands.bot_has_permissions(manage_roles=False)
    async def on_guild_join(self, guild):
        mute_role_found = self.get_mute_role(guild)

        if mute_role_found is False:
            await self.setup_mute_role(guild)

    @commands.command(usage="{0}addmod @DJ#3333", aliases=["admin", "mod"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def addmod(self, ctx, member: discord.Member):
        """
        Add a moderator to the list of server moderators
        """
        desc = f"{member.mention} is already a mod."
        guild_mods = await Guilds.get_mods(member.guild.id)

        if member.id not in guild_mods:
            desc = f"Added {member.mention} to mods!"

            await Guilds.add_mod(member)
        elif member.bot is True:
            desc = "You cannot add **bots** as moderators."

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(usage="{0}delmod @DJ#3333", aliases=["unmod", "unadmin"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def delmod(self, ctx, member: discord.Member):
        """
        Remove a moderator from the server
        """
        desc = f"{member.mention} is not a mod."
        guild_mods = await Guilds.get_mods(member.guild.id)

        if member.id in guild_mods and member.guild_permissions.administrator:
            desc = "Those with admin permissions cannot be removed from mods."
        elif member.guild_permissions.administrator is False:
            desc = f"Deleted {member.mention} from mods!"

            await Guilds.del_mod(member)

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(usage="{0}mods", aliases=["listmods", "admins", "m"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def mods(self, ctx):
        """
        Displays all of the mods within a server


        **Note**: this also shows the server owner and those with the
        "administrator" permission
        """
        desc = ""
        guild_mods = await Guilds.get_mods(ctx.guild.id)
        guild_mods = guild_mods + [m.id for m in ctx.guild.members
                                   if m.guild_permissions.administrator
                                   and m.bot is False]

        for member_id in guild_mods:
            member_found = ctx.guild.get_member(member_id)

            if member_found is None:
                await Guilds.del_mod(member_found)
                guild_mods.remove(member_id)

                continue
            desc += f"{member_found.mention}\n"

        await ctx.send(embed=create_embed("Mods", desc))

    @commands.command(usage="{0}warn @DJ#3333 chat filter bypass",
                      aliases=["w"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        """
        Warn a member for the specified reason
        """
        title = "Warning"
        desc = f"{member.mention} has been warned"
        message = (f"You were warned in **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        member_warnings = await Guilds.get_warnings(member)
        fields = {
            "ID": f"`{member.id}`",
            "Moderator": f"{ctx.author.mention}",
            "Reason": reason,
            "Total Warnings": f"`{len(member_warnings)+1}`"
        }

        await Guilds.add_warn(member, ctx.author, reason)
        await ctx.send(embed=create_embed(title, desc, fields=fields))
        await self.dm(member, message, reason)

    @commands.command(usage="{0}warnings\n{0}warnings @DJ#3333",
                      aliases=["warns", "getwarns"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def warnings(self, ctx, member: discord.Member = None):
        """
        Displays the warnings for the given member in the server this command
        is used in
        """
        member = member or ctx.author
        no_mod = "User left"
        member_warnings = await Guilds.get_warnings(member)
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
    @commands.has_permissions(manage_guild=True)
    async def clearwarns(self, ctx, member: discord.Member):
        """
        Remove all of the warnings for the given member in the server
        this command is used in
        """
        warnings, _ = await Guilds.clear_warns(member)
        append = warnings == 1 and "warn" or "warns"
        desc = f"Cleared {warnings} {append}"

        embed = create_embed(title="Clearwarns", desc=desc)
        await ctx.send(embed=embed)

    @commands.command(usage="{0}perms\n{0}perms @DJ#3333",
                      aliases=["permissions"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def perms(self, ctx, member: discord.Member = None):
        """
        Show the permissions given to the specified member

        Note: if the member has the special "administrator" permission or is
        the owner of the server this command is used in, these permissions
        will be shown and by default every permission will be granted.
        """
        member = member or ctx.author
        title = "Permissions"
        desc = ""
        perms = ctx.channel.permissions_for(member)
        perm_values = []

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

    @commands.command(usage="{0}mute @DJ#3333 10m")
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_roles=True, mute_members=True)
    async def mute(self, ctx, member: discord.Member, time: int):
        """
        Prevent the given member from communicating in the server this command
        is used in
        """
        timestamp = datetime.timedelta(seconds=time)
        title = "Mute"
        desc = f"Muted **{member}** for `{timestamp}`"
        limit = 60**2 * 12  # 12h
        mute_role = self.get_mute_role(ctx.guild)
        is_muted = mute_role in member.roles

        if mute_role is None:
            mute_role = await self.setup_mute_role(ctx.guild)

        if time <= 0 or time > limit or is_muted:
            return

        self.mutes.setdefault(member.id, {
            "time": time,
            "task": self.on_second.start(ctx, member)
        })

        await member.add_roles(mute_role)
        await member.edit(mute=True)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}unmute @DJ#3333")
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_roles=True, mute_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """
        Allow a member to communicate once again after previously being muted
        """
        member_data = self.mutes.get(member.id)

        if member_data is not None or member_data.get("time") > 1:
            member_data["time"] = 1

    @commands.command(usage="{0}kick @DJ#3333\n"
                            "{0}kick @DJ#3333 3 warnings", aliases=["k"])
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
        message = (f"You were kicked from **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        fields = {}

        if reason is not None:
            fields["Reason"] = reason

        if member.id == ctx.author.id:
            desc = "You **cannot** kick yourself!"
        elif self.calculate_perms(ctx.author, member) is False:
            desc = ("You **cannot** kick someone who has a higher role than "
                    "you!")
        elif ctx.author.guild_permissions.administrator is False:
            desc = ("You **cannot** kick someone if you do not sufficient "
                    "permissions!")
        else:
            fields = {
                "ID": f"`{member.id}`",
                "Moderator": str(ctx.author)
            }

            await member.kick(reason=reason)
            await self.dm(member, message, reason)

        embed = create_embed(title, desc, fields=fields)

        await ctx.send(embed=embed)

    @commands.command(usage="{0}ban @DJ#3333\n{0}ban @DJ#3333 raiding",
                      aliases=["b"])
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: Union[discord.Member, discord.User], *,
                  reason=None):
        """
        Bans the given member or member ID from the server - if a reason is
        given, this will be displayed in the audit logs
        """
        title = user.display_name
        function = ctx.guild.ban
        desc = f"{user.mention} was banned"
        message = (f"You were banned from **{ctx.guild}** by "
                   f"**{str(ctx.author)}**")
        args = [
            user
        ]
        kwargs = {
            "reason": reason
        }
        fields = {}

        if reason is not None:
            fields["Reason"] = reason

        await ctx.send(type(user) is discord.Member)
        if type(user) is discord.Member:
            function = user.ban
            args = []

        if ctx.author.id == user.id:
            desc = "You **cannot** ban yourself!"
        elif (type(user) is discord.Member and
              self.calculate_perms(ctx.author, user) is False):
            desc = "You **cannot** ban someone who has a higher role than you!"
        elif ctx.author.guild_permissions.administrator is False:
            desc = ("You **cannot** ban someone if you do not have the "
                    "\"administrator\" permission!")
        else:
            fields = {
                "ID": f"`{user.id}`",
                "Moderator": ctx.author.display_name
            }

            await function(*args, **kwargs)
            await self.dm(user, message, reason)

        embed = create_embed(title, desc, fields=fields)
        await ctx.send(embed=embed)

    @commands.command(usage="{0}bans\n"
                            "{0}bans 464446709146320897")
    @bot.checks.delete()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def bans(self, ctx, guild_id: int = None):
        """
        List the members that have been banned with the given reason
        associated with their ban (if any) within the server this command is
        used in
        """
        message = ""
        selected_guild = ctx.guild

        if guild_id is not None and guild_id != ctx.guild.id:
            guild_found = self.bot.get_guild(guild_id)

            if guild_found:
                # check if both rammus and the user are in the guild
                author_found = guild_found.get_member(ctx.author.id)
                self_found = guild_found.me is not None

                if author_found and self_found:
                    is_owner = guild_found.owner.id == author_found.id
                    is_admin = author_found.guild_permissions.ban_members

                    if is_owner or is_admin:
                        selected_guild = guild_found

        bans = await selected_guild.bans()

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
            user = await self.bot.fetch_user(user_id)
            title = getattr(user, "display_name", user.name)
            desc = f"{user.mention} has been unbanned!"
            await ctx.guild.unban(user)

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}purge 500\n"
                            "{0}purge @DJ#3333 500")
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(read_message_history=True,
                                  manage_messages=True)
    async def purge(self, ctx, member: Optional[discord.Member], number: int):
        """
        Deletes messages in bulk with a maximum of 500 message to delete at a
        time
        """
        messages = number == 1 and "message" or "messages"
        title = "Purge"
        desc = f"Successfully purged `{number}` {messages}"
        deleted = 0
        limit = 500
        desc = None

        def check(message):
            nonlocal deleted

            if deleted == number:
                return False

            if member is None:
                deleted += 1
                return True
            elif message.author == member:
                deleted += 1
                return True

        if number < 0 or number > limit:
            desc = (f"`Number` must be a number equal or up to `{limit}`, not "
                    f"{number}")

            return await ctx.send(embed=create_embed(title, desc))

        while deleted < number:
            purged = await ctx.channel.purge(before=ctx.message, check=check)
            deleted += len(purged)

        embed = create_embed(title, desc)
        embed.add_field(name="Note", value=f"`This message will be deleted "
                                           f"automatically in 8s.`")
        message = await ctx.send(desc, embed=embed)

        await message.delete(delay=8)

    @commands.group(usage="{0}role @DJ#3333 @Community\n"
                          "{0}role @DJ#3333 @Community @Subscriber\n"
                          "{0}role @DJ#3333 \"Comm Member\" Subscriber",
                    invoke_without_command=True, aliases=["setrole"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member,
                   roles: commands.Greedy[discord.Role]):
        """
        Toggle the specified role(s) for the given member - if member has the
        role then it is removed, otherwise it is added


        **Note**: for Rammus to assign any roles to any member it must:

        • At least have a higher role than the role(s) it is trying to assign
        • Have the appropriate permissions (manage roles) to do as such

        Not following through with these conditions will cause Rammus to fail
        role assignment
        """
        title = ctx.invoked_with.title()
        desc = ""
        roles_to_add = []
        roles_to_remove = []
        failed_roles = []
        roles = [r for r in roles if r.is_default() is False and
                 r.managed is False]

        for role in roles:
            if self.calculate_perms(ctx.author, role) is False:
                failed_roles.append(role)
            elif role in member.roles:
                roles_to_remove.append(role)
            else:
                roles_to_add.append(role)

        # if given no valid roles, end task early to prevent wasted resources
        if roles_to_add == roles_to_remove == failed_roles == EMPTY_LIST:
            desc = "No valid roles given"

            return await ctx.send(embed=create_embed(title, desc))

        add_str = (", ").join([r.mention for r in roles_to_add])
        remove_str = (", ").join([r.mention for r in roles_to_remove])
        fail_str = (", ").join([r.mention for r in failed_roles])

        if roles_to_add != EMPTY_LIST:
            desc += f"Added {add_str} to **{member}**\n"
        if roles_to_remove != EMPTY_LIST:
            desc += f"Removed {remove_str} from **{member}**\n"
        if failed_roles != EMPTY_LIST:
            desc += f"Failed to assign {fail_str} to **{member}**"

        await member.add_roles(*roles_to_add)
        await member.remove_roles(*roles_to_remove)
        await ctx.send(embed=create_embed(title, desc))

    @role.group(name="add", usage="{0}role add @DJ#3333 @Community\n"
                                  "{0}role add @DJ#3333 @Community "
                                  "@Subscriber\n"
                                  "{0}role add @DJ#3333 \"Comm Member\" "
                                  "Subscriber",
                invoke_without_command=True)
    async def add_role(self, ctx, member: discord.Member,
                       roles: commands.Greedy[discord.Role]):
        """
        Add the specified role(s) to the given member
        """
        title = ctx.invoked_with.title()
        desc = ""
        roles_to_add = []
        failed_roles = []

        for role in roles:
            if self.calculate_perms(ctx.author, role) is False:
                failed_roles.append(role)
            elif role not in member.roles:
                roles_to_add.append(role)

        roles_str = (", ").join([r.mention for r in roles_to_add])
        failed_str = (", ").join([r.mention for r in failed_roles])

        if roles_to_add != EMPTY_LIST:
            desc += f"Added {roles_str} to **{member}**\n"
        if failed_roles != EMPTY_LIST:
            desc += f"Failed to assign {failed_str} to **{member}**"

        await member.add_roles(*roles_to_add)
        await ctx.send(embed=create_embed(title, desc))

    @role.group(name="remove", usage="{0}role remove @DJ#3333 @Community\n"
                                     "{0}role remove @DJ#3333 @Community "
                                     "@Subscriber\n"
                                     "{0}role remove @DJ#3333 \"Comm Member\" "
                                     "Subscriber",
                invoke_without_command=True, aliases=["del"])
    async def remove_role(self, ctx, member: discord.Member,
                          roles: commands.Greedy[discord.Role]):
        """
        Remove the specified role(s) from the given member
        """
        title = ctx.invoked_with.title()
        desc = ""
        roles_to_remove = []
        failed_roles = []

        for role in roles:
            if self.calculate_perms(ctx.author, role) is False:
                failed_roles.append(role)
            else:
                roles_to_remove.append(role)

        roles_str = (", ").join([r.mention for r in roles_to_remove])
        failed_str = (", ").join([r.mention for r in failed_roles])

        if roles_to_remove != EMPTY_LIST:
            desc += f"Removed {roles_str} from **{member}**\n"
        if failed_roles != EMPTY_LIST:
            desc += f"Failed to assign {failed_str} to **{member}**"

        await member.remove_roles(*roles_to_remove)
        await ctx.send(embed=create_embed(title, desc))

    @role.group(usage="{0}role join @Community\n"
                      "{0}role join @Community @Subscriber\n"
                      "{0}role join \"Comm Member\" Subscriber",
                invoke_without_command=True)
    async def join(self, ctx, roles: commands.Greedy[discord.Role] = []):
        """
        When a member joins, allow the member to receive the given role

        Note: You can give multiple roles and this also works without having
        to mention the roles - those with spaces must be surrounded in
        quotation marks, e.g. ("Role With Spaces")
        """
        try:
            title = "Join Role" + (len(roles) == 1 and "" or "s")
        except TypeError:
            title = "Join Roles"

        action = (roles != [] and "Removed" or "Set")
        desc = f"{action} {title.lower()}"

        await Guilds.set_join_roles(ctx.guild.id, roles)
        await ctx.send(embed=create_embed(title, desc))

    @join.command(name="add", usage="{0}role join add @Community\n"
                                    "{0}role join add @Community @Subscriber\n"
                                    "{0}role join add \"Comm Member\" "
                                    "Subscriber")
    async def add_join_role(self, ctx, roles: commands.Greedy[discord.Role]):
        """
        Add the specified roles to the list of roles given to a member when
        they join this server
        """
        title = ctx.invoked_with.title()
        desc = "Added "
        join_roles = await Guilds.get_roles(ctx.guild.id)
        roles_to_add = []

        for role in roles:
            if role.id in join_roles:
                continue

            desc += f"{role.mention} "
            roles_to_add += [role.id]

        join_roles += roles_to_add
        desc += f"to the join roles (**{len(join_roles)}**)"

        await Guilds.set_join_roles(ctx.guild.id, join_roles)
        await ctx.send(embed=create_embed(title, desc))

    @join.command(name="remove", usage="{0}role join remove @Community\n"
                                       "{0}role join remove @Community "
                                       "@Subscriber\n"
                                       "{0}role join remove \"Comm Member\" "
                                       "Subscriber",
                  aliases=["del"])
    async def remove_join_role(self, ctx,
                               roles: commands.Greedy[discord.Role]):
        """
        Remove the specified roles from the list of roles given to a member
        when they join this server
        """
        title = ctx.invoked_with.title()
        desc = "Removed "
        join_roles = await Guilds.get_roles(ctx.guild.id)

        for role in roles:
            if role.id not in join_roles:
                continue

            desc += f"{role.mention} "
            join_roles.remove(role.id)

        desc += f"from the join roles (**{len(join_roles)}**)"

        await Guilds.set_join_roles(ctx.guild.id, join_roles)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}nick @DJ#3333\n{0}nick @DJ#3333 big loser",
                      aliases=["setnick"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nick=None):
        """
        Set the nickname of the given member to the given nickname

        Note: the nickname must be between 2 - 32 characters long, any
        nicknames shorter/longer than this will not work.
        """
        desc = (f"Successfully changed {member.mention}'s name to "
                f"**{nick}**!")

        if nick is None:
            desc = f"Successfully reset {member.mention}'s name!"
        elif len(nick) < 2 or len(nick) > 32:
            desc = (f"**{nick}** is too short/long, it must be between 2 - 32 "
                    f"characters long")

        await member.edit(nick=nick)
        await ctx.send(embed=create_embed("Nick", desc))

    @commands.command(usage="{0}slowmode 15\n{0}slowmode")
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, delay: Union[int, str] = 15):
        """
        Toggle and control slowmode for the channel this command is used in
        """
        if type(delay) is str:
            delay = self.resolve_delay(delay)

        title = "Slowmode has been enabled"
        desc = f"You can type a new message every `{delay}` seconds!"

        if delay in List.delays:
            delays = []

            for i, v in enumerate(List.delays):
                delay = f"`{v}`"

                if i < len(List.delays):
                    delay = f"`{v},`"

                delays.append(delay)

            embed = create_embed(title="Delays", desc=("\n").join(delays))

            try:
                await ctx.author.send(embed=embed)
            except discord.Forbidden:
                pass

            title = f"The given delay is invalid"
            desc = "A list of valid delays has been DMed to you!"
        elif ctx.channel.slowmode_delay == delay:
            title = f"The slowmode delay is already at {delay}s"
            desc = "There is no need to change it!"
        # "List.delays[-1]" is the last and the highest delay you can use
        elif delay < 0 or delay > List.delays[-1]:
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
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        """
        Set up a channel for member join/leave messages to be sent in
        """
        title = "Join/Leave Channel"
        action = channel is None and "Removed" or "Set"
        desc = (f"{action} join/leave channel")
        channel = channel is not None and channel.id or channel

        await Guilds.set_channel(ctx.guild.id, channel)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}joinmsg\n{0}joinmsg Welcome!",
                      aliases=["joinmessage"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def joinmsg(self, ctx, *, message=None):
        """
        Set up a message to be sent whenever a member joins your server
        """
        title = "Join Message"
        action = message is None and "Removed" or "Set"
        desc = f"{action} join message"

        await Guilds.set_message(ctx.guild.id, message, join=True)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}leavemsg\n{0}leavemsg Goodbye!",
                      aliases=["leavemessage"])
    @bot.checks.delete()
    @commands.has_permissions(manage_guild=True)
    async def leavemsg(self, ctx, *, message=None):
        """
        Set up a message to be sent whenever a member leaves your server
        """
        title = "Leave Message"
        action = message is None and "Removed" or "Set"
        desc = f"{action} leave message"

        await Guilds.set_message(ctx.guild.id, message, leave=True)
        await ctx.send(embed=create_embed(title, desc))

    @commands.command(usage="{0}rainbowify\n"
                            "{0}rainbowify --reverse",
                      aliases=["rainbowroles", "rainbow"])
    @bot.checks.is_guild_owner()
    @bot.checks.delete()
    async def rainbowify(self, ctx, *args):
        """
        Change the colours of all unmanaged (non-bot) roles to match a
        rainbow theme


        **Note**: only the server owner can use this command. Once this is
        done it *cannot* be set back, you have been warned.

        Appending "--reverse" to the end of the command will allow the colours
        to form a negative rainbow theme (instead of starting at red, the
        theme will start at blue).
        """
        args = list(map(str.lower, args))
        title = ctx.invoked_with.title()
        desc = ("**Note**: once this is done it *cannot* be set back, you "
                "have been warned.")
        embed = create_embed(title, desc)
        message = await ctx.send(embed=embed)

        await message.add_reaction("👍")
        await message.add_reaction("👎")

        def check(reaction, member):
            return (member == ctx.author and
                    reaction.emoji in ["👍", "👎"] and True or False)

        try:
            reaction, member = await self.bot.wait_for("reaction_add",
                                                       timeout=15.0,
                                                       check=check)
        except asyncio.TimeoutError:
            desc = "Timed out"
        else:
            await message.clear_reactions()

            if reaction.emoji == "👍":
                desc = "In Progress..."
                embed = create_embed(title, desc)
                init_val = "--reverse" in args and 0.5 or 0
                roles = [r for r in ctx.guild.roles
                         if r.is_default() is False and r.managed is False]

                await message.edit(embed=embed)

                for i, role in enumerate(reversed(roles)):
                    hue = i == 0 and init_val or i / (len(roles) + init_val)
                    colour = discord.Colour(0).from_hsv(hue, 1, 1)

                    if role.colour.value != colour.value:
                        await role.edit(colour=colour)

                role_str = "role" + (len(roles) == 1 and "" or "s")
                desc = f"Successfully changed **{len(roles):,}** {role_str}! 😊"
            else:
                desc = "Cancelled"
        finally:
            embed = create_embed(title, desc)

            await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
