import datetime
import re

import asyncio
import discord
from discord.ext import commands

from bot.db import Ask
from bot.utils import send_with_embed


class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.regex = re.compile(r"\s+in\s+(\d+h\s?)?(\d+m\s?)?(\d+s)?")

    def resolve_time(self, message):
        match_found = self.regex.search(message)
        time = []

        if match_found:
            for unit in match_found.groups():
                if unit is not None:
                    unit = int(re.sub(r"[hms\s]", "", unit))
                else:
                    unit = 0

                time.append(unit)

        obj = {}
        obj["hours"], obj["minutes"], obj["seconds"] = time

        return obj

    async def create_reminder(self, member, message, hours=0, minutes=0,
                              seconds=0):
        message = self.regex.sub("", message)
        delta = datetime.timedelta(hours=hours, minutes=minutes,
                                   seconds=seconds)

        await asyncio.sleep(delta.seconds)

        try:
            await member.send(f":timer: **Reminder**\n{message}")
        except discord.Forbidden:
            pass

    @commands.command(usage="{0}ask what is 2+2?")
    async def ask(self, ctx, *, question):
        """
        Ask a question and either get an answer if it has been answered before
        or get the question ID you can use to supply an answer.
        """
        question = question.lower()
        title = "Question"
        desc = f"\"{question}\""
        fields = {}
        entry = await Ask.get_entry(question=question)

        # not a question, explain question pre-requisites
        if not question.endswith("?"):
            title = "Invalid Question"
            desc = ("You either did not ask a question or forgot to add "
                    "`?` to the end of your question.")
        # is a question, given no data
        elif entry is None:
            entry = await Ask.create_entry(ctx, question)
            entry_id = entry.get("id")
            title = "Question not asked before"
            desc = (f"You can add your own answer by using `>add {entry_id}` "
                    f"with your answer at the end of it.")
        # is a question, given entry
        elif entry.get("answer") is None:
            entry_id = entry.get("id")
            title = "No answer for question"
            desc = (f"The question has been asked but there is no answer. "
                    f"Use `>add {entry_id}` with your answer at the end to "
                    f"add one.")
        # given question, answer found
        else:
            fields.update({
                "answer": entry.get("answer")
            })

        await send_with_embed(ctx, title, desc, fields=fields)

    @commands.command(usage="{0}answer 1 2+2 is 2")
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def answer(self, ctx, id: int, *, answer):
        """
        Set the answer to the question's ID. If you do not know how to get a
        question's ID, do `>help ask`
        """
        title = "Answer has been added"
        desc = None
        entry = await Ask.get_entry(id=str(id))

        # entry does not exist
        if entry is None:
            title = "Question with ID does not exist"
            desc = ("Try using `>ask` then your question to get a valid entry "
                    "for a question.")
        # entry exists, answer exists
        elif entry.get("answer") is not None:
            entry = await Ask.get_entry(answer=answer)
            id = entry.get("id")
            title = f"Answer already exists with ID `{id}`"
            desc = "You cannot overwrite an answer."
        # entry exists, answer does not, add answer to entry
        elif (await Ask.add_answer_to(entry, answer)) is False:
            title = "Failed to add answer"

        await send_with_embed(ctx, title, desc)

    @commands.command(usage="{0}reminder do homework in 30m\n"
                            "{0}reminder head to Joe's place in 2h 10m")
    async def reminder(self, ctx, *, message):
        """
        Sets a reminder with the given message for the user in the given
        amount of time

        Note: you are reminded through DMs so if you have Rammus blocked,
        this feature will not work.
        """
        title = "Reminder"
        desc = f"Set a reminder for \"{message}\""
        time = self.resolve_time(message)

        if any(time) is False:
            return

        self.bot.loop.create_task(
            self.create_reminder(ctx.author, message, **time)
        )
        await send_with_embed(ctx, title, desc)


def setup(bot):
    bot.add_cog(Community(bot))
