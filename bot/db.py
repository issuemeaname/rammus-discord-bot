import atexit
import datetime
import json
import os
import time

import discord


class AskDatabase:
    def __init__(self):
        self.path = r"bot/files/ask.json"

        if self.db_exists():
            self._db = dict()

            with open(self.path, "w") as f:
                json.dump(self._db, f, indent=4)
        else:
            with open(self.path, "r") as f:
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


class ModDatabase:
    def __init__(self):
        self.path = "bot/files/warns.json"
        self.get_warns = self.get_warnings  # alias

        with open(self.path, "r") as db:
            self._db = json.load(db)

    def save(self):
        with open(self.path, "w") as db:
            json.dump(self._db, db, indent=4)

    def get_guild(self, guild_id):
        guild_id = str(guild_id)
        default = {
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
        self.save()

        return member_warnings  # return member's list of warnings

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
        member_warnings.clear()
        self.save()

        return member_warnings  # return new list of warnings

    def add_mod(self, member: discord.Member):
        mods = self.get_mods(member.guild.id)
        mods.append(member.id)
        self.save()

        return mods

    def del_mod(self, member: discord.Member):
        mods = self.get_mods(member.guild.id)
        mods.remove(member.id)
        self.save()

        return mods


Ask = AskDatabase()
Mod = ModDatabase()


@atexit.register
def save_all():
    Ask.save()
    Mod.save()

    print("Saved all databases")
