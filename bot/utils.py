import os
import textwrap
import traceback
from typing import Union

import discord

from bot.resources import COLOUR
from bot.resources import FOOTER


def clear_screen(_os, post_message: str = None, end: str = None):
    _os = _os.lower()
    commands = {
        "windows": "cls",
        "mac": "clear",
        "linux": "clear"
    }

    os.system(commands[_os])

    if post_message:
        print(post_message, end=end or "\n")


def create_embed(title=None, desc=None, fields: dict = None,
                 image: Union[discord.File, str] = None):
    embed = discord.Embed(title=title, description=desc, colour=COLOUR)
    embed.set_footer(text=FOOTER)

    if fields is not None:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)

    if type(image) is str:
        embed.set_image(url=image)
    elif type(image) is discord.File:
        embed.set_image(url=f"attachment://{image.filename}")

    return embed


def get_tb_message(error, newline="\n"):
    newline = newline or ""
    tracebacks = ("").join(traceback.format_tb(error.__traceback__))

    return textwrap.dedent(tracebacks) + newline + (f"{type(error).__name__}: "
                                                    f"{error}")


def wrap(text, type="py"):
    wrapper = textwrap.TextWrapper(1992-(len(type)), drop_whitespace=False,
                                   replace_whitespace=False)
    blocks = []

    for block in wrapper.wrap(text):
        blocks.append(f"```{type}\n{block}\n```")

    return blocks
