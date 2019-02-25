"""
Place images, file references and content here.

Feel free to use bot.utils or the discord library to return files if necessary.
"""
import os
from string import ascii_lowercase

import discord


VERSION = "2.2"
COLOUR = discord.Colour(0).from_rgb(208, 103, 129)
FOOTER = "issuemeaname | MIT Copyright © 2018"

INVITE = "https://tinyurl.com/InviteRammus"
SERVER = "https://tinyurl.com/RammusServer"
GUILD = SERVER  # alias

OWNERS = [173225726139564032, 402593497942720512]  # fill with member IDs

PACER_TEST = ("The FitnessGram™ Pacer Test is a multistage aerobic capacity "
              "test that progressively gets more difficult as it continues. "
              "The 20 meter pacer test will begin in 30 seconds. Line up at "
              "the start. The running speed starts slowly, but gets faster "
              "each minute after you hear this signal. [beep] A single lap "
              "should be completed each time you hear this sound. [ding] "
              "Remember to run in a straight line, and run as long as "
              "possible. The second time you fail to complete a lap before "
              "the sound, your test is over. The test will begin on the word "
              "start. On your mark, get ready, start.")


def _get_cogs():
    path = r"bot/cogs"
    cog_path = "bot.cogs"
    cogs = []

    for obj in os.listdir(path):
        origin = os.path.join(os.getcwd(), path, obj)

        if os.path.isfile(origin):
            obj = os.path.splitext(obj)[0]

            if obj.startswith("_") is False:
                obj_path = (".").join([cog_path, obj])

                cogs.append(obj_path)
    return sorted(cogs) or None


def _get_hugs():
    path = r"bot\images\hug"
    hugs = []

    for obj in os.listdir(path):
        file = discord.File(os.path.join(os.getcwd(), path, obj),
                            filename="hug.gif")
        hugs.append(file)
    return hugs or None


class Path:
    root = "bot"
    cogs = _get_cogs()


class List:
    new = {}
    hugs = _get_hugs()
    letters = list(ascii_lowercase)
    cringe = [
        "My dad is builderman and he will ban you!"
    ]
    digits = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine"
    }
    morse = {  # encrypting by default
        " ": "/",
        "&": ".-...",
        "'": ".----.",
        "@": ".--.-.",
        ")": "-.--.-",
        "(": "-.--.",
        ":": "---...",
        ",": "--..--",
        "=": "-...-",
        "!": "-.-.--",
        ".": ".-.-.-",
        "-": "-....-",
        "+": ".-.-.",
        "\"": ".-..-.",
        "?": "..--..",
        "/": "-..-.",
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--.."
    }
