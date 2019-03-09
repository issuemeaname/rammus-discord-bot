import string
from typing import Union

# import discord
from discord.ext import commands

from bot.resources import List
from bot.utils import create_embed


class TextManipulation(commands.Cog, name="text_manipulation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def split(self, ctx, *, message):
        await ctx.send((" ").join(message))

    @commands.command()
    async def reverse(self, ctx, *, message):
        await ctx.send(("").join(reversed(message)))

    @commands.command()
    async def clap(self, ctx, *, message):
        await ctx.send((":clap:").join(message.split(" ")) + ":clap:")

    @commands.command()
    async def morse(self, ctx, mode, *, message):
        mode = mode.upper()
        title = "Encrypted"
        desc = ""
        append = " "
        unknown = "?"
        chars = List.morse

        if mode == "DECRYPT":
            title = "Decrypted"
            append = ""
            unknown = "..--.."
            message = message.split()
            chars = {v: k for k, v in chars.items()}

        for char in message:
            char = char.upper()

            if char in chars:
                desc += chars.get(char)
            else:
                desc += chars.get(unknown)

            desc += append

        await ctx.send(embed=create_embed(title, desc))

    @commands.command()
    async def caesar(self, ctx, shift: int, *, message):
        desc = "Caesar Cipher"
        caeser = shift == 0 and message or ""

        if shift == 0:
            caeser = message
        else:
            for orig_char in message:
                char = orig_char.lower()

                if char not in string.ascii_letters:
                    caeser += char
                else:
                    index = (List.letters.index(char) + shift) % 26

                    if orig_char == char:
                        # original char is lowercase by default
                        char = List.letters[index]
                    else:
                        char = List.letters[index]

                    caeser += char

        fields = {
            "Original": message,
            "Shifted": caeser,
            "Shift": f"`{shift:,}`"
        }

        await ctx.send(embed=create_embed(desc=desc, fields=fields))

    @commands.command()
    async def binary(self, ctx, mode, *, message: Union[int, str]):
        mode = mode.upper()
        title = "Encrypted"
        desc = ""
        append = " "

        if mode == "DECRYPT":
            title = "Decrypted"
            append = ""
            message = message.split()

        for char in message:
            if mode == "DECRYPT":
                value = int(char, base=2)
                desc += chr(value)
            else:
                asc = ord(char)  # character ascii value
                desc += bin(asc)[2:]

            desc += append

        await ctx.send(embed=create_embed(title, desc))


def setup(bot):
    bot.add_cog(TextManipulation(bot))
