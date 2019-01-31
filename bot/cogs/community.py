# import discord
from discord.ext import commands

from bot.db import Ask
from bot.utils import embed


class Community:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage=">ask question")
    async def ask(self, ctx, *, question):
        """
        Ask a question and either get an answer if it has been answered before
        or get the question ID you can use to supply an answer.
        """
        question = question.lower()
        title = "Question"
        desc = f"\"{question}\""
        answer_given = False
        entry = Ask.get_entry(question=question)

        # not a question, explain question pre-requisites
        if not question.endswith("?"):
            title = "Invalid Question"
            desc = ("You either did not ask a question or forgot to add "
                    "`?` to the end of your question.")
        # is a question, given no data
        elif entry is None:
            entry = Ask.create_entry(ctx, question)
            id = entry.get("id")
            title = "Question not asked before"
            desc = (f"You can add your own answer by using `>add {id}` "
                    f"with your answer at the end of it.")
        # is a question, given entry
        elif entry.get("answer") is None:
            id = entry.get("id")
            title = "No answer for question"
            desc = (f"The question has been asked but there is no answer. "
                    f"Use `>add {id}` with your answer at the end to "
                    f"add one.")
        # given question, answer found
        else:
            answer_given = entry.get("answer")

        embed_ = embed(title, desc)

        if answer_given is not False:
            answer = entry.get("answer")

            embed_.add_field(name="Answer", value=f"\"{answer}\"")

        await ctx.send(embed=embed_)

    @commands.command()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def answer(self, ctx, id: int, *, answer):
        """
        Set the answer to the question's ID. If you do not know how to get a
        question's ID, do `>help ask`
        """
        title = "Answer has been added"
        desc = None
        entry = Ask.get_entry(id=str(id))

        # entry does not exist
        if entry is None:
            title = "Question with ID does not exist"
            desc = ("Try using `>ask` then your question to get a valid entry "
                    "for a question.")
        # entry exists, answer exists
        elif entry.get("answer") is not None:
            entry = Ask.get_entry(answer=answer)
            id = entry.get("id")
            title = f"Answer already exists with ID `{id}`"
            desc = "You cannot overwrite an answer."
        # entry exists, answer does not, add answer to entry
        elif Ask.add_answer_to(entry, answer) is False:
            title = "Failed to add answer"

        await ctx.send(embed=embed(title, desc))


def setup(bot):
    bot.add_cog(Community(bot))
