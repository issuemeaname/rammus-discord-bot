import atexit
import datetime
import json
import os
import time

import discord

from bot.prefix import DEFAULT


class AskDatabase:
    def __init__(self):
        self.path = r"bot/files/ask.json"

        if self.db_exists():
            self._db = dict()

            directory = os.path.dirname(self.path)
            os.makedirs(directory)

            with open(self.path, "w+") as f:
                json.dump(self._db, f, indent=4)
        else:
            with open(self.path, "r+") as f:
                self._db = json.load(f)

    # function loads pre-init - check if db file exists
    def db_exists(self):
        return os.path.exists(self.path) is False or \
               os.path.getsize(self.path) == 0

    def save(self):
        with open(self.path, "w") as db:
            json.dump(self._db, db, indent=4)

    def _get_current_time(self):
        return datetime.datetime.now().strftime("%d %b %Y @ %I:%M %p (GMT)")

    def get_entry(self, question=None, answer=None, id=None):
        query = question or answer or str(id)
        query_type = None

        if question:
            query_type = "question"
        elif answer:
            query_type = "answer"
        else:
            query_type = "id"

        for id, entry in self._db.items():
            queried = entry.get(query_type)

            if str(queried) == query:
                return entry
        return None

    def create_entry(self, ctx, question):
        id = len(self._db)
        entry = {
            "id": id,  # backwards compatibility & integer id
            "question": question,
            "author_id": ctx.author.id,
            "created_at": self._get_current_time()
        }

        return self._db.setdefault(str(id), entry)

    def add_answer_to(self, entry, answer):
        try:
            entry.setdefault("answer", answer)
        except Exception:
            return False
        else:
            return True


class GuildsDatabase:
    def __init__(self):
        self.path = "bot/files/guilds.json"
        self.get_warns = self.get_warnings  # alias
        self.message_features = {
            "{member}": None,
            "{@member}": "mention",
            "{guild}": "guild.name",
            "{server}": "guild.name"
        }

        directory = os.path.dirname(self.path)
        os.makedirs(directory)

        with open(self.path, "w+") as db:
            self._db = json.load(db)

    def save(self):
        with open(self.path, "w") as db:
            json.dump(self._db, db, indent=4)

    # getters
    def get_guild(self, guild_id):
        guild_id = str(guild_id)
        default = {
            "prefix": DEFAULT,
            "mods": [],
            "members": {}
        }

        return self._db.setdefault(guild_id, default)

    def get_member(self, guild_id, member_id):
        member_id = str(member_id)
        guild = self.get_guild(member_id)
        members = guild.get("members")

        return members.setdefault(member_id, [])

    def get_mods(self, guild_id):
        guild = self.get_guild(guild_id)

        return guild.get("mods")

    def get_warnings(self, member: discord.Member):
        member_warnings = self.get_member(member.guild.id, member.id)

        return member_warnings  # return member's list of warnings

    def get_prefix(self, guild_id):
        guild = self.get_guild(guild_id)

        return guild.setdefault("prefix", DEFAULT)

    def get_messages(self, guild_id):
        guild = self.get_guild(guild_id)
        default = {
            "join": None,
            "leave": None
        }

        return guild.setdefault("messages", default)

    def get_channel(self, guild_id):
        guild = self.get_guild(guild_id)
        default = None

        return guild.setdefault("channel", default)

    def get_roles(self, guild_id):
        guild = self.get_guild(guild_id)
        default = {
            "join": None,
            "mods": None
        }

        return guild.setdefault("roles", default)

    # setters/manipulators
    def add_warn(self, member: discord.Member, moderator: discord.Member,
                 reason):
        member_warnings = self.get_member(member.guild.id, member.id)
        warning = {
            "moderator": moderator.id,
            "reason": reason,
            "created": int(time.time())
        }
        member_warnings.append(warning)
        self.save()

        return warning  # return issued warning

    def clear_warns(self, member: discord.Member):
        member_warnings = self.get_member(member.guild.id, member.id)
        warnings_num = len(member_warnings)
        member_warnings.clear()
        self.save()

        return warnings_num, member_warnings  # return new list of warnings

    def add_mod(self, member: discord.Member):
        mods = self.get_mods(member.guild.id)
        mods.append(member.id)
        self.save()

        return mods  # return newly added mod

    def del_mod(self, member: discord.Member):
        mods = self.get_mods(member.guild.id)
        mods.remove(member.id)
        self.save()

        return mods  # return deleted mod

    def set_prefix(self, guild_id, prefix):
        guild = self.get_guild(guild_id)
        guild["prefix"] = prefix
        self.save()

        return prefix  # return new prefix

    def get_message(self, guild_id, join=False, leave=False):
        messages = self.get_messages(guild_id)
        key = join and "join" or leave and "leave" or None

        if key is not None:
            return messages.get(key)  # return server's join/leave message
        return None

    def set_message(self, guild_id, message, join=False, leave=False):
        messages = self.get_messages(guild_id)
        key = join and "join" or leave and "leave" or None

        if key is not None:
            messages[key] = message

        self.save()

        return message  # return new join/leave message

    def set_channel(self, guild_id, channel):
        guild = self.get_guild(guild_id)
        guild["channel"] = channel
        self.save()

        return channel  # return new join/leave message channel

    def set_join_roles(self, guild_id, join_roles):
        roles = self.get_roles(guild_id)
        join_roles = [r.id for r in join_roles]
        roles["join"] = join_roles
        self.save()

        return join_roles  # return names of new member join roles


Ask = AskDatabase()
Guilds = GuildsDatabase()


@atexit.register
def save_all():
    Ask.save()
    Guilds.save()

    print("Saved all databases")
