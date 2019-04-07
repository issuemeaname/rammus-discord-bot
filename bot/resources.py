"""
Place images, file references and content here.

Feel free to use bot.utils or the discord library to return files if necessary.
"""
import os
from string import ascii_lowercase

import discord

from bot.db import Guilds
from bot.prefix import DEFAULT


VERSION = "8.0"
FOOTER = "issuemeaname | MIT Copyright © 2018"

OWNERS = [173225726139564032, 202373732067442690]  # fill with member IDs

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


async def command_prefix(bot, message):
    prefix = DEFAULT

    if message.guild is not None:
        guild_id = str(message.guild.id)
        prefix = Guilds.get_prefix(guild_id)

    return [bot.user.mention + " ", prefix]


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


class Colours:
    RED = discord.Colour(0).from_rgb(208, 102, 129)
    ORANGE = discord.Colour(0).from_rgb(208, 129, 102)
    GREEN = discord.Colour(0).from_rgb(129, 208, 103)


class Service:
    GITHUB = "https://github.com/issuemeaname/rammus-discord-bot"
    INVITE = "https://tinyurl.com/InviteRammus"
    SERVER = "https://tinyurl.com/RammusServer"
    TRELLO = "https://trello.com/b/yKDNUGdI/rammus-discord-bot"

    GUILD = SERVER  # alias


class List:
    new = {}
    hugs = _get_hugs()
    letters = list(ascii_lowercase)
    cringe = [
        "My dad is builderman and he will ban you!"
    ]
    statuses = [
        "Facerolling",
        "AP Nuke",
        ">commands",
        "Ok.",
        "in Iron IV"
    ]
    permissions = [
        "add_reactions",
        "attach_files",
        "ban_members",
        "change_nickname",
        "connect",
        "create_instant_invite",
        "deafen_members",
        "embed_links",
        "kick_members",
        "manage_channels",
        "manage_emojis",
        "manage_messages",
        "manage_nicknames",
        "manage_roles",
        "manage_webhooks",
        "mention_everyone",
        "move_members",
        "mute_members",
        "priority_speaker",
        "read_message_history",
        "send_messages",
        "send_tts_messages",
        "speak",
        "use_voice_activation",
        "view_audit_log"
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
    responses_8ball = {
        "Positive": [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes."
        ],
        "Vague": [
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again."
        ],
        "Negative": [
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
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
