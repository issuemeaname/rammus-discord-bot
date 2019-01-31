import os
import textwrap
import traceback

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


def embed(title=None, desc=None, image: discord.File = None):
    embed_ = discord.Embed(title=title, description=desc, colour=COLOUR)
    embed_.set_footer(text=FOOTER)

    if image is not None:
        embed_.set_image(url=f"attachment://{image.filename}")

    return embed_


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
