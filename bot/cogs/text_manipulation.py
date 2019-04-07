import string
from typing import Union

# import discord
from discord.ext import commands

from bot.resources import List
from bot.utils import create_embed


class TextManipulation(commands.Cog, name="Text Manipulation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="{0}split AESTHETIC")
    async def split(self, ctx, *, message):
        """
        Splits the message up by adding spaces between every character
        """
        await ctx.send((" ").join(message))

    @commands.command(usage="{0}reverse race car")
    async def reverse(self, ctx, *, message):
        """
        Sends the same message back but reversed
        """
        await ctx.send(("").join(reversed(message)))

    @commands.command(usage="{0}clap Thank you")
    async def clap(self, ctx, *, message):
        """
        Separates each character in the message with :clap:
        """
        await ctx.send((":clap:").join(message.split(" ")) + ":clap:")

    @commands.command(usage="{0}bigtext We need to build a wall")
    async def bigtext(self, ctx, *, message):
        """
        Make your messages stand out
        """
        bigtext = ""
        append = " "

        for i, char in enumerate(message):
            char = char.lower()

            if i+1 == len(message):
                append = ""

            if char.isdigit():
                char = f":{List.digits[char]}:"
            elif char.isalpha():
                char = f":regional_indicator_{char}:"
            elif char == " ":
                char = char*2
            else:
                char = ""

            bigtext += char + append

        await ctx.send(bigtext)

    @commands.command(usage="{0}morse ENCRYPT Hello\n"
                            "{0}morse DECRYPT -... -.-- .")
    async def morse(self, ctx, mode, *, message):
        """
        With the given mode, encrypts/decrypts the given message from
        text - morse and vice versa

        Available modes: ENCRYPT, DECRYPT
        """
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

    @commands.command(usage="{0}caeser 5 Meet me in the yard.\n"
                            "{0}caeser -5 Rjjy rj ns ymj dfwi.")
    async def caesar(self, ctx, shift: int, *, message):
        """
        Shifts every letter of the message by the given shift as a means of
        encryption

        Note: decryption is also possible if you use the same shift but
        negative. If the shift you used to encrypt a message is e.g. 6, to
        decrypt that same message you would use -6 as the given shift.
        """
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
                        char = List.letters[index].upper()

                    caeser += char

        fields = {
            "Original": message,
            "Shifted": caeser,
            "Shift": f"`{shift:,}`"
        }

        await ctx.send(embed=create_embed(desc=desc, fields=fields))

    @commands.command(usage="{0}binary ENCRYPT Hi\n"
                            "{0}binary DECRYPT 1001000 1101001")
    async def binary(self, ctx, mode, *, message: Union[int, str]):
        """
        Converts every character in the message to binary numbers or every
        binary number to readable text with the given mode

        Available modes: ENCRYPT, DECRYPT
        """
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
                desc += bin(asc)[2:].zfill(8)

            desc += append

        await ctx.send(embed=create_embed(title, desc))


def setup(bot):
    bot.add_cog(TextManipulation(bot))
