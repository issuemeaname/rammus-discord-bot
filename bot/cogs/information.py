from typing import Union

import discord
from discord.ext import commands

from bot.API import Datamuse
from bot.prefix import PREFIX
from bot.resources import INVITE
from bot.resources import Path
from bot.resources import SERVER
from bot.resources import VERSION
from bot.utils import embed
from bot.utils import wrap


class Information:
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

        await ctx.send(embed=embed(title, text))

    @commands.command()
    async def prefix(self, ctx):
        await ctx.send(f"You can mention me or use the `{PREFIX}` prefix.")

    @commands.command()
    async def help(self, ctx, name=None):
        """
        Displays information for a particular command, such as parameters,
        instructions, alternate names
        """
        command = self.command_exists(name)
        title = ""
        desc = ""
        args = None

        # list all commands
        if name is None:
            data = {}
            message = ""

            for command in self.bot.commands:
                if command.hidden:
                    continue

                name = command.name
                cog_name = command.cog_name or "Uncategorised"
                cog = data.get(cog_name)

                if data.get(cog_name) is None:
                    data[cog_name] = []

                if name not in cog:
                    cog.append(name)

            for cog, commands_list in data.items():
                message += f"{cog}:\n"

                for name in sorted(commands_list):
                    message += " " * 2 + f"{name}\n"

            for block in wrap(message, type=""):
                await ctx.send(block)

            return
        elif command is None or command.hidden:
            title = "That command does not exist!"
            desc = "How about trying one that does?"
        else:
            title = command.name.capitalize()
            desc = command.help
            args = {
                "Category": command.cog_name,
                "Parameters": (", ").join(command.clean_params.keys()),
                "Usage": f"`{command.usage}`",
                "Aliases": command.aliases or "None"
            }

        embed_ = embed(title, desc)

        if args is not None:
            for name, value in args.items():
                embed_.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed_)

    @commands.command()
    async def creator(self, ctx):
        await ctx.send(f"{self.bot.owner.mention} is the one who created me.")

    @commands.command(aliases=["guild"])
    async def server(self, ctx):
        await ctx.send(SERVER + " :heart:")

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(INVITE + " :heart:")

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

        await ctx.send(embed=embed(image=image))

    @commands.command(aliases=["thesaurus"])
    async def synonym(self, ctx, word):
        word = word.lower()
        synonyms = await Datamuse.get_synonyms(word)
        embed_ = embed(desc="Thesaurus")

        embed_.add_field(name="Word", value=word, inline=False)
        embed_.add_field(name="Synonyms", value=(", ").join(synonyms))

        await ctx.send(embed=embed_)

    @commands.command()
    async def whois(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = (", ").join(map(str, member.roles))
        embed_ = embed(str(member), member.mention)

        embed_.add_field(name="Status", value=str(member.status).title())
        embed_.add_field(name="Joined", value=str(member.joined_at))
        embed_.add_field(name="Registered", value=str(member.created_at))
        embed_.add_field(name="Roles", value=roles)


def setup(bot):
    bot.add_cog(Information(bot))
