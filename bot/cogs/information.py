from typing import Union

import discord
from discord.ext import commands

from bot.API import Datamuse
from bot.prefix import PREFIX
from bot.resources import INVITE
from bot.resources import Path
from bot.resources import SERVER
from bot.resources import VERSION
from bot.utils import create_embed
from bot.utils import wrap


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_exists(self, queried=None):
        if queried is None:
            return

        for cog_name in Path.cogs:
            if cog_name == queried:
                return cog_name
        return None

    def command_exists(self, queried=None):
        if queried is None:
            return

        for command in self.bot.commands:
            if command.name == queried:
                return command
        return None

    @commands.command()
    async def version(self, ctx):
        title = "Rammus"
        text = f"Version: **{VERSION}**"

        await ctx.send(embed=create_embed(title, text))

    @commands.command()
    async def prefix(self, ctx):
        await ctx.send(f"You can mention me or use the `{PREFIX}` prefix.")

    @commands.command(name="help")
    async def _help(self, ctx, name):
        """
        Displays information for a particular command, such as parameters,
        instructions, alternate names
        """
        pass

    @commands.command()
    async def creator(self, ctx):
        await ctx.send(f"{self.bot.owner.mention} is the one who created me.")

    @commands.command(aliases=["guild"])
    async def server(self, ctx):
        await ctx.send(embed=create_embed("Server", f"{SERVER} :green_heart:"))

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(embed=create_embed("Invite", f"{INVITE} :green_heart:"))

    @commands.command()
    async def id(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        await ctx.send(member.id)

    @commands.command()
    async def avatar(self, ctx, member: Union[discord.Member, str] = None):
        image = None

        if isinstance(member, str):
            if member.lower() in ["guild", "server"]:
                image = ctx.guild.icon_url_as()
        else:
            member = member or ctx.author
            image = member.avatar_url_as()

        await ctx.send(embed=create_embed(image=image))

    @commands.command(aliases=["thesaurus"])
    async def synonym(self, ctx, word):
        word = word.lower()
        synonyms = await Datamuse.get_synonyms(word)
        embed = create_embed(desc="Thesaurus")

        embed.add_field(name="Word", value=word, inline=False)
        embed.add_field(name="Synonyms", value=(", ").join(synonyms))

        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx, member: Union[discord.Member, str] = None):
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


def setup(bot):
    bot.add_cog(Information(bot))
