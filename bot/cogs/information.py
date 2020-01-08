import sys
from typing import Union

import discord
from discord.ext import commands

import bot.checks
from bot.API import Datamuse
from bot.db import Guilds
from bot.prefix import DEFAULT
from bot.resources import List
from bot.resources import VERSION
from bot.utils import create_embed
from bot.utils import generate_invite_url
from bot.utils import send_with_embed


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_cogs = [
            "Error Handler",
            "Owner",
            "Personal",
            "Test"
        ]
        self.info = {
            "github": "https://github.com/issuemeaname/rammus-discord-bot",
            "server": "https://discordapp.com/invite/N2SJy9H",
            "trello": "https://trello.com/b/yKDNUGdI/rammus-discord-bot",
            "invite": generate_invite_url(self.bot),
            "creator": f"{self.bot.owner.mention} is the one who created me."
        }

    # async def send_info(self, ctx, service=None):
    #     title = ctx.invoked_with.title()
    #     invite = generate_invite_url(self.bot)
    #     service = List.services.get(service, invite)
    #     desc = f"[Here]({service}) :green_heart:"

    #     await send_with_embed(ctx, title, desc)

    @commands.command(usage="{0}version", aliases=["v"])
    async def version(self, ctx, py: str = False):
        """
        Shows the current version of Rammus
        """
        version = VERSION

        if py and py.lower() == "py":
            python = sys.version.split()[0]
            version = f"Python {python}"

        title = "Rammus"
        desc = f"Version: **{version}**"

        await send_with_embed(ctx, title, desc)

    # @commands.command(usage="{0}creator")
    # async def creator(self, ctx):
    #     """
    #     Shows who created Rammus
    #     """
    #     await ctx.send(
    #         f"{self.bot.owner.mention} is the one who created me."
    #     )

    @commands.command(name="BLACKLIST", aliases=["creator", "invite", "github",
                                                 "server", "trello"])
    async def _send_info(self, ctx):
        """
        Send information based on invoked alias
        """
        title = ctx.invoked_with.title()
        info = self.info.get(ctx.invoked_with)
        desc = f"[Here]({info}) \U0001f49a"

        await send_with_embed(ctx, title, desc)

    # @commands.command(usage="{0}github")
    # async def github(self, ctx):
    #     """
    #     Sends the personal GitHub repository for Rammus
    #     """
    #     await self.send_info(ctx, "GITHUB")

    # @commands.command(usage="{0}invite", aliases=["i"])
    # async def invite(self, ctx):
    #     """
    #     Sends the personal invite URL for Rammus
    #     """
    #     await self.send_info(ctx)

    # @commands.command(usage="{0}server", aliases=["guild", "s", "g"])
    # async def server(self, ctx):
    #     """
    #     Sends the personal server for Rammus
    #     """
    #     await self.send_info(ctx, "SERVER")

    # @commands.command(usage="{0}trello", aliases=["t"])
    # async def trello(self, ctx):
    #     """
    #     Sends the personal Trello board for Rammus
    #     """
    #     await self.send_info(ctx, "TRELLO")

    @commands.command(usage="{0}ping")
    async def ping(self, ctx):
        """
        Show Rammus's latency when using Discord
        """
        title = "Ping"
        desc = f"Latency of `{int(self.bot.latency*1000):,}ms`"

        await ctx.send(embed=create_embed(title, desc))

    @commands.command(name="id", usage="{0}id\n"
                                       "{0}id @DJ#3333\n"
                                       "{0}id #general\n"
                                       "{0}id @Community @Owners #general\n"
                                       "{0}id \"Comm Member\" Owners")
    async def _id(self, ctx, *objs: commands.Greedy[Union[discord.Member,
                  discord.TextChannel, discord.Role]]):
        """
        Displays either your own or the given member's unique Discord ID

        **Note**: this command does not support giving server IDs so if you
        would like to retrieve that then feel free to use the `info` command:

        `>info server`
        """
        fields = {}
        objs = objs or [ctx.author]

        for obj in objs:
            if type(obj) is str:
                if obj.lower() in ["server", "guild"]:
                    obj = ctx.guild
                else:
                    return

            fields.setdefault(f"ID for {obj}", f"`{obj.id}`")

        embed = create_embed(fields=fields, author=ctx.author)

        await ctx.send(embed=embed)

    @commands.command(usage="{0}avatar\n"
                            "{0}avatar @DJ#3333\n"
                            "{0}avatar guild", aliases=["a"])
    async def avatar(self, ctx, member: Union[discord.Member, str] = None):
        """
        Sends either your own or the given member's profile picture
        """
        member = member or ctx.author
        is_str = type(member) is str
        lowered = is_str and member.lower() or False
        is_keyword = lowered in ["guild", "server"]
        image = ""

        if is_str and is_keyword:
            member = ctx.guild
        elif is_str and not is_keyword:
            member_found = discord.utils.get(ctx.guild.members, name=member,
                                             display_name=member)

        title = str(member)

        if hasattr(member, "avatar_url_as"):
            image = member.avatar_url_as(static_format="png", size=256)
        elif hasattr(member, "icon_url_as"):
            image = member.icon_url_as(static_format="png", size=256)
        elif member_found is None:
            title = str(ctx.author)
            desc = f'No member exists with the name "{member}"'

        if image:
            desc = f"[Link]({image})"

        embed = create_embed(title, desc, image=image)

        await ctx.send(embed=embed)

    @commands.command(usage="{0}synonym complete", aliases=["thesaurus"])
    async def synonym(self, ctx, word):
        """
        Get all of the synonyms for the given word if there are any that
        Rammus can find
        """
        word = word.lower()
        synonyms = await Datamuse.get_synonyms(word)
        value = None

        if synonyms is None:
            value = "`None`"
        else:
            value = (", ").join(synonyms)

        embed = create_embed(title="Word", desc=word)
        embed.add_field(name="Synonyms", value=value)
        await ctx.send(embed=embed)

    @commands.group(usage="{0}prefix", aliases=["p"],
                    invoke_without_command=True)
    async def prefix(self, ctx):
        """
        Displays the prefix used in this server
        """
        prefix = await Guilds.get_prefix(ctx.guild.id)
        title = "Prefix"
        desc = f"The prefix for **{ctx.guild}** is `{prefix}`"

        await ctx.send(embed=create_embed(title, desc))

    @prefix.command(name="set", usage="{0}prefix set !")
    @bot.checks.delete()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, *, prefix=None):
        """
        Set Rammus's prefix in the server, give no prefix for it to be reset
        back to the default prefix (`>`)

        **Note**: as of now the character limit for the prefix is 2^5 or 32
        but this may change in the somewhat near future.
        """
        title = f"Prefix set"
        desc = f"Set **{ctx.guild.name}**'s prefix to `{prefix}`"
        limit = 2**5
        guild_prefix = await Guilds.get_prefix(ctx.guild.id)

        if prefix is None:
            # im sure theres a better way to do this...
            prefix = DEFAULT
            desc = f"Reset prefix to `{prefix}` for **{ctx.guild.name}**!"

            await Guilds.set_prefix(ctx.guild.id, prefix)
        elif len(prefix) > limit:
            desc = (f"`{prefix}` is too long to be a valid prefix. Please use "
                    f"a prefix that is less than or equal to {limit} "
                    f"characters.")
        elif guild_prefix == prefix:
            desc = (f"`{prefix}` is already the prefix for "
                    f"**{ctx.guild.name}**!")
        else:
            await Guilds.set_prefix(ctx.guild.id, prefix)

        await ctx.send(embed=create_embed(title, desc))

    @commands.group(usage="{0}info\n"
                          "{0}info @DJ#3333\n"
                          "{0}info server",
                    invoke_without_command=True)
    async def info(self, ctx, member: discord.Member = None):
        """
        Displays all of the information for either yourself, the given member
        or the server this command is used in
        """
        member = member or ctx.author
        member_format = "%a %d %b %Y %I:%M:%S %p"
        desc = ctx.guild.name
        thumbnail = member.avatar_url
        roles = [r.mention for r in member.roles if r.is_default() is False]
        statuses = {
            discord.Status.online: "Online",
            discord.Status.dnd: "Busy",
            discord.Status.idle: "AFK",
            discord.Status.offline: "Offline"
        }
        fields = {
            "ID": f"`{member.id}`",
            "Status": statuses[member.status],
            "Mobile": member.is_on_mobile() and "✅" or "❌",
            "Joined": member.joined_at.strftime(member_format),
            "Registered": member.created_at.strftime(member_format),
            f"Roles `({len(roles)})`": (" ").join(roles)
        }

        embed = create_embed(desc=desc, fields=fields, inline=True,
                             author=member, thumbnail=thumbnail)

        await ctx.send(embed=embed)

    @info.command(name="server", aliases=["guild"],
                  usage="{0}info server\n"
                        "{0}info guild")
    async def info_server(self, ctx):
        guild = ctx.guild
        thumbnail = guild.icon_url
        guild_format = "%m/%d/%y %I:%M:%S %p"
        desc = f"Owned by {guild.owner}"
        humans = list(filter(lambda m: m.bot is False, guild.members))
        bots = list(filter(lambda m: m.bot, guild.members))
        fields = {
            "ID": f"`{guild.id}`",
            "Owner": guild.owner.mention,
            "Region": f"**{str(guild.region).upper()}**",
            "Created": guild.created_at.strftime(guild_format),
            "Members": f"{guild.member_count:,} "
                       f"(**{len(humans):,}** People, "
                       f"**{len(bots)}** Bots",
            "Emojis": len(guild.emojis),
            "Channels": f"{len(guild.channels):,} "
                        f"(**{len(guild.text_channels):,}** Text, "
                        f"**{len(guild.voice_channels):,}** VCs, "
                        f"**{len(guild.categories):,}** Categories)",
            "Roles": len(guild.roles) - 1,
            "Large": guild.large and "✅" or "❌"
        }

        embed = create_embed(desc=desc, fields=fields, inline=True,
                             author=guild, thumbnail=thumbnail)

        await ctx.send(embed=embed)

    @commands.command(name="commands", usage="{0}commands")
    async def rammus_commands(self, ctx):
        """
        Shows all of the commands under their respective categories
        """
        title = ctx.command.name.title()
        fields = {}

        for cog_name in sorted(self.bot.cogs):
            cog = self.bot.get_cog(cog_name)
            id_given = getattr(cog, "_GUILD", False)
            commands = cog.get_commands()

            if cog_name in self.ignored_cogs:
                continue

            if id_given and id_given == ctx.guild.id:
                cog_name = f"[EXCLUSIVE] {cog_name}"

            if len(commands) == 0:
                commands = ["`None`"]
            else:
                commands = [c.name.title() for c in commands]

            fields.setdefault((", ").join(commands))

        await send_with_embed(ctx, title, fields=fields)

    @commands.command(name="help", usage="{0}help say", aliases=["h"])
    async def _help(self, ctx, name: str = None):
        """
        Displays information for a particular command, such as parameters,
        explanations, alternate names, usage instructions, etc.
        """
        if name is None:
            return await ctx.invoke(self.bot.get_command("commands"))

        command = self.bot.get_command(name)
        prefix = await Guilds.get_prefix(ctx.guild.id)
        title = ""
        desc = ""
        fields = {}

        if command is None:
            title = ctx.command.title()
            desc = (f"`{prefix}{name}` does not exist as a command. Please "
                    f"try one that does.")
        else:
            id_given = getattr(command.cog, "guild_id", 0)

            if id_given == ctx.guild.id:
                title = command.name.title()
                desc = f"{command.help}" if command.help else "`Not provided`"
                aliases = list(map(str.capitalize, command.aliases))
                aliases = (", ").join(aliases) or "None"
                arguments = map(str.title, command.clean_params.keys())
                arguments = (", ").join(arguments) or "None"
                usage = command.usage.format(prefix) or "Not provided"
                usage = ("\n").join(map(("`{}`").format, usage.split("\n")))

                fields.update({
                    "Aliases": aliases,
                    "Category": command.cog_name.title(),
                    "Arguments": arguments,
                    "Usage": usage
                })

        await send_with_embed(ctx, title, desc, fields=fields)


def setup(bot):
    bot.add_cog(Information(bot))
