import os
import textwrap
import traceback
from typing import Union

import discord

from bot.resources import Colours
from bot.resources import FOOTER


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


def create_embed(title=None, desc=None, colour=Colours.GREEN,
                 fields: dict = None, image: Union[discord.File, str] = None,
                 author: discord.Member = None):
    embed = discord.Embed(title=title, description=desc, colour=colour)
    embed.set_footer(text=FOOTER)

    if fields is not None:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)

    if type(image) is discord.File:
        embed.set_image(url=f"attachment://{image.filename}")
    elif type(image) is str:
        embed.set_image(url=image)

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
