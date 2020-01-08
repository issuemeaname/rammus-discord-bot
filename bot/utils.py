import datetime
import os
import textwrap
import traceback
from typing import Union

import discord

from bot.resources import Colours
from bot.resources import PERMISSIONS


def clear_screen(system, message: str = None, end: str = None):
    system = system.lower()
    commands = {
        "windows": "cls",
        "mac": "clear",
        "linux": "clear"
    }

    os.system(commands[system])

    if message:
        print(message, end=end or "\n")


def get_license():
    return f"issuemeaname | MIT Copyright © {datetime.datetime.now().year}"


def create_embed(title=None, desc=None, inline=False, colour=Colours.GREEN,
                 fields: dict = {}, author: discord.Member = None,
                 image: Union[discord.File, discord.Asset] = "",
                 thumbnail: Union[discord.File, discord.Asset] = ""):
    footer = get_license()
    embed = discord.Embed(title=title, description=desc, colour=colour)
    embed.set_footer(text=footer)

    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=inline)

    if type(image) is discord.File:
        image = f"attachment://{image.filename}"
    if type(thumbnail) is discord.File:
        thumbnail = f"attachment://{image.filename}"

    embed.set_image(url=image)
    embed.set_thumbnail(url=thumbnail)

    if author:
        embed.set_author(name=str(author), icon_url=author.avatar_url)

    return embed


def get_tb_message(error, newline="\n"):
    newline = newline or ""
    tracebacks = ("").join(traceback.format_tb(error.__traceback__))

    return textwrap.dedent(tracebacks) + newline + (f"{type(error).__name__}: "
                                                    f"{error}")


def wrap(text, type="py", embed=False, no_blocks=False):
    total = embed and 2048 or 2000
    block_size = 8
    blocks = []
    wrapper = textwrap.TextWrapper(total-block_size-(len(type)),
                                   drop_whitespace=False,
                                   replace_whitespace=False)

    for block in wrapper.wrap(text):
        blocks.append(f"```{type}\n{block}\n```")

    return blocks


def generate_invite_url(bot):
    return discord.utils.oauth_url(bot.user.id, PERMISSIONS)


async def send_with_embed(ctx, *args, **kwargs):
    return await ctx.send(embed=create_embed(*args, **kwargs))
