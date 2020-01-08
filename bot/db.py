import aiofiles
import asyncio
import datetime
import json
import os
import time

import discord

from bot.prefix import DEFAULT


loop = asyncio.get_event_loop()


class AskDatabase:
    def __init__(self):
        self.path = r"bot/files/ask.json"

        loop.create_task(self.setup())

    async def setup(self):
        if self.db_exists():
            self._db = dict()

            async with aiofiles.open(self.path, "w") as db:
                dump = json.dumps(self._db, indent=4)

                await db.write(dump)
        else:
            async with aiofiles.open(self.path, "r") as db:
                data = await db.read()

                self._db = json.loads(data)

    async def save(self):
        async with aiofiles.open(self.path, "w") as db:
            dump = json.dumps(self._db, indent=4)

            await db.write(dump)

    # function loads pre-init - check if db file exists
    def db_exists(self):
        return (os.path.exists(self.path) is False or
                os.path.getsize(self.path) == 0)

    def _get_current_time(self):
        return datetime.datetime.now().strftime("%d %b %Y @ %I:%M %p (GMT)")

    # I 100% believe that there is a better way to do this
    async def get_entry(self, question=None, answer=None, id=None):
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

    async def create_entry(self, ctx, question):
        id = len(self._db)
        entry = {
            "id": id,  # backwards compatibility & integer id
            "question": question,
            "author_id": ctx.author.id,
            "created_at": self._get_current_time()
        }
        await self.save()

        return self._db.setdefault(str(id), entry)

    async def add_answer_to(self, entry, answer):
        try:
            entry.setdefault("answer", answer)
        except Exception:
            return False
        else:
            return True

        await self.save()


class GuildsDatabase:
    def __init__(self):
        self._db = {}
        self.path = "bot/files/guilds.json"
        self.get_warns = self.get_warnings  # alias
        self.message_features = {
            "{member}": None,
            "{@member}": "mention",
            "{guild}": "guild.name",
            "{server}": "guild.name"
        }

        loop.create_task(self.setup())

    async def setup(self):
        if os.path.exists(self.path) is False:
            async with aiofiles.open(self.path, "w") as db:
                dump = json.dumps(self._db, indent=4)

                await db.write(dump)
        else:
            async with aiofiles.open(self.path, "r") as db:
                data = await db.read()

                self._db = json.loads(data)

    async def save(self):
        async with aiofiles.open(self.path, "w") as db:
            dump = json.dumps(self._db, indent=4)

            await db.write(dump)

    # getters
    async def get_guild(self, guild_id):
        guild_id = str(guild_id)
        default = {
            "prefix": DEFAULT,
            "mods": [],
            "members": {}
        }

        return self._db.setdefault(guild_id, default)

    async def get_member(self, guild_id, member_id):
        member_id = str(member_id)
        guild = await self.get_guild(member_id)
        members = guild.get("members")

        return members.setdefault(member_id, [])

    async def get_mods(self, guild_id):
        guild = await self.get_guild(guild_id)

        return guild.get("mods")

    async def get_warnings(self, member: discord.Member):
        member_warnings = await self.get_member(member.guild.id, member.id)

        return member_warnings  # return member's list of warnings

    async def get_prefix(self, guild_id):
        guild = await self.get_guild(guild_id)

        return guild.setdefault("prefix", DEFAULT)

    async def get_messages(self, guild_id):
        guild = await self.get_guild(guild_id)
        default = {
            "join": None,
            "leave": None
        }

        return guild.setdefault("messages", default)

    async def get_channel(self, guild_id):
        guild = await self.get_guild(guild_id)
        default = None

        return guild.setdefault("channel", default)

    async def get_roles(self, guild_id):
        guild = await self.get_guild(guild_id)
        default = {
            "join": None,
            "mods": None
        }

        return guild.setdefault("roles", default)

    # setters/manipulators
    async def add_warn(self, member: discord.Member, moderator: discord.Member,
                       reason):
        member_warnings = await self.get_member(member.guild.id, member.id)
        warning = {
            "moderator": moderator.id,
            "reason": reason,
            "created": int(time.time())
        }
        member_warnings.append(warning)
        await self.save()

        return warning  # return issued warning

    async def clear_warns(self, member: discord.Member):
        member_warnings = await self.get_member(member.guild.id, member.id)
        warnings_num = len(member_warnings)
        member_warnings.clear()
        await self.save()

        return warnings_num, member_warnings  # return new list of warnings

    async def add_mod(self, member: discord.Member):
        mods = await self.get_mods(member.guild.id)
        mods.append(member.id)
        await self.save()

        return mods  # return newly added mod

    async def del_mod(self, member: discord.Member):
        mods = await self.get_mods(member.guild.id)
        mods.remove(member.id)
        await self.save()

        return mods  # return deleted mod

    async def set_prefix(self, guild_id, prefix):
        guild = await self.get_guild(guild_id)
        guild["prefix"] = prefix
        await self.save()

        return prefix  # return new prefix

    async def get_message(self, guild_id, mtype):
        messages = await self.get_messages(guild_id)
        await self.save()

        return messages.get(mtype)  # return server's join/leave message

    async def set_message(self, guild_id, message, mtype):
        messages = await self.get_messages(guild_id)
        messages[mtype] = message
        await self.save()

        return message  # return new join/leave message

    async def set_channel(self, guild_id, channel):
        guild = await self.get_guild(guild_id)
        guild["channel"] = channel
        await self.save()

        return channel  # return new join/leave message channel

    async def set_join_roles(self, guild_id, join_roles):
        roles = await self.get_roles(guild_id)
        join_roles = [r.id for r in join_roles if type(r) is discord.Role]
        roles["join"] = join_roles
        await self.save()

        return join_roles  # return names of new member join roles


async def _log_error(error):
    async with asyncio.open("log.txt", "w") as f:
        await f.write(error)


Ask = AskDatabase()
Guilds = GuildsDatabase()


async def save_all_dbs():
    await Ask.save()
    await Guilds.save()
