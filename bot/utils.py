import os
import textwrap
import traceback

import discord

from bot.resources import COLOUR
from bot.resources import FOOTER


"""
[ ] Add custom TextWrapper variable from owner cog
"""


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


def embed(title=None, desc=None, **kwargs):
    return discord.Embed(title=title, description=desc, colour=COLOUR,
                         **kwargs).set_footer(text=FOOTER)


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
