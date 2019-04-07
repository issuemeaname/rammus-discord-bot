from typing import Union

import discord
from discord.ext import commands

from bot.API import Datamuse
from bot.db import Guilds
from bot.resources import Service
from bot.resources import VERSION
from bot.utils import create_embed


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_cogs = [
            "Error Handler",
            "Owner",
            "Personal",
            "Test"
        ]

    async def send_info(self, ctx, github=False, invite=False, server=False,
                        trello=False):
        desc = ""

        if github:
            desc = f"[Here]({Service.GITHUB}) :purple_heart:"
        elif invite:
            desc = f"[Here]({Service.INVITE}) :green_heart:"
        elif server:
            desc = f"[Here]({Service.SERVER}) :heart:"
        elif trello:
            desc = f"[Here]({Service.TRELLO}) :blue_heart:"

        embed = create_embed(title=ctx.invoked_with.title(), desc=desc)
        await ctx.send(embed=embed)

    @commands.command(usage="{0}version", aliases=["v"])
    async def version(self, ctx):
        """
        Shows the current version of Rammus
        """
        title = "Rammus"
        text = f"Version: **{VERSION}**"

        await ctx.send(embed=create_embed(title, text))

    @commands.command(usage="{0}prefix", aliases=["p"])
    async def prefix(self, ctx):
        """
        Displays the prefix used in this server
        """
        prefix = Guilds.get_prefix(ctx.guild.id)

        await ctx.send(f"You can mention me or use the `{prefix}` prefix.")

    @commands.command(usage="{0}creator")
    async def creator(self, ctx):
        """
        Shows who created Rammus
        """
        await ctx.send(f"{self.bot.owner.mention} is the one who created me.")

    @commands.command(usage="{0}github")
    async def github(self, ctx):
        """
        Sends the personal GitHub repository for Rammus
        """
        await self.send_info(ctx, github=True)

    @commands.command(usage="{0}invite", aliases=["i"])
    async def invite(self, ctx):
        """
        Sends the personal invite URL for Rammus
        """
        await self.send_info(ctx, invite=True)

    @commands.command(usage="{0}server", aliases=["guild", "s", "g"])
    async def server(self, ctx):
        """
        Sends the personal server for Rammus
        """
        await self.send_info(ctx, server=True)

    @commands.command(usage="{0}trello", aliases=["t"])
    async def trello(self, ctx):
        """
        Sends the personal Trello board for Rammus
        """
        await self.send_info(ctx, trello=True)

    @commands.command(usage="{0}id\n{0}id @DJ#3333")
    async def id(self, ctx, member: discord.Member = None):
        """
        Displays either your own or the given member's unique Discord ID
        """
        if member is None:
            member = ctx.author

        embed = create_embed(title="ID", desc=f"`{member.id}`", author=member)
        await ctx.send(embed=embed)

    @commands.command(usage="{0}avatar\n{0}avatar @DJ#3333", aliases=["a"])
    async def avatar(self, ctx, member: Union[discord.Member, str] = None):
        """
        Sends either your own or the given member's profile picture
        """
        image = None

        if type(member) is str:
            if member.lower() in ["guild", "server"]:
                image = ctx.guild.icon_url_as()
        else:
            member = member or ctx.author
            image = member.avatar_url_as()

        await ctx.send(embed=create_embed(image=image))

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

    @commands.command(usage="{0}info\n{0}info @DJ#3333\n{0}info server")
    async def info(self, ctx, member: Union[discord.Member, str] = None):
        """
        Displays all of the information for either yourself, the given member
        or the server this command is used in
        """
        member = member or ctx.author
        embed = None
        desc = None
        image = None
        fields = None
        author = None
        member_format = "%a %d %b %Y %I:%M:%S %p"
        guild_format = "%m/%d/%y %I:%M:%S %p"

        if type(member) is discord.Member:
            desc = ctx.guild.name
            author = str(member)
            image = member.avatar_url
            roles = [r.mention for r in member.roles
                     if r.is_default() is False]
            statuses = {
                discord.Status.online: "Online",
                discord.Status.dnd: "Busy",
                discord.Status.idle: "AFK",
                discord.Status.offline: "Offline"
            }
            fields = {
                "ID": f"`{member.id}`",
                "Status": statuses[member.status],
                "Mobile": member.is_on_mobile() and "Yes" or "No",
                "Joined": member.joined_at.strftime(member_format),
                "Registered": member.created_at.strftime(member_format),
                f"Roles `({len(roles)})`": (" ").join(roles)
            }
        elif type(member) is str and member.upper() in ["GUILD", "SERVER"]:
            guild = ctx.guild
            desc = f"Owned by {guild.owner}"
            author = guild.name
            image = guild.icon_url
            fields = {
                "ID": f"`{guild.id}`",
                "Owner": guild.owner.mention,
                "Region": f"**{str(guild.region).upper()}**",
                "Created": guild.created_at.strftime(guild_format),
                "Members": guild.member_count,
                "Emojis": len(guild.emojis),
                "Channels": f"{len(guild.channels)} "
                            f"(**{len(guild.text_channels)}** Text, "
                            f"**{len(guild.voice_channels)}** VCs)",
                "Categories": len(guild.categories),
                "Roles": len(guild.roles) - 1
            }
        else:
            return

        embed = create_embed(desc=desc)
        embed.set_author(name=author, icon_url=image)
        embed.set_thumbnail(url=image)

        for name, value in fields.items():
            embed.add_field(name=name, value=value)

        await ctx.send(embed=embed)

    @commands.command(name="{0}commands", usage="commands")
    async def _commands(self, ctx):
        """
        Shows all of the commands under their respective categories
        """
        fields = {}

        for cog_name in sorted(self.bot.cogs):
            if cog_name in self.ignored_cogs:
                continue
            cog = self.bot.get_cog(cog_name)
            commands = cog.get_commands()

            if len(commands) == 0:
                commands = ["`None`"]
            else:
                commands = [c.name.title() for c in commands]

            fields[cog_name] = (", ").join(commands)

        embed = create_embed(fields=fields)
        await ctx.send(embed=embed)

    @commands.command(name="help", usage="{0}help say", aliases=["h"])
    async def _help(self, ctx, name):
        """
        Displays information for a particular command, such as parameters,
        explanations, alternate names, usage instructions, etc.
        """
        command = self.bot.get_command(name)
        prefix = Guilds.get_prefix(ctx.guild.id)
        title = None
        desc = None
        fields = None
        print(command.cog, command is not None)

        if command is not None:
            title = command.name.title()
            desc = f"{command.help}" or "`Not provided`"
            aliases = [a.title() for a in command.aliases if len(a) > 1]
            aliases = command.aliases and (", ").join(aliases) or "None"
            arguments = [a.title() for a in command.clean_params.keys()]
            arguments = (", ").join(arguments)
            usage = f"`{command.usage.format(prefix)}`" or "`Not provided`"
            fields = {
                "Aliases": aliases,
                "Category": command.cog_name.title(),
                "Arguments": arguments,
                "Usage": usage
            }
        else:
            title = "Help"
            desc = (f"`{prefix}{name}` does not exist as a command. Please "
                    f"try one that does.")

        await ctx.send(embed=create_embed(title, desc, fields=fields))


def setup(bot):
    bot.add_cog(Information(bot))
