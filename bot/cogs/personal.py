import random

import discord
from discord.ext import commands

import bot.checks
from bot.resources import PACER_TEST


class Personal:
    def __init__(self, bot):
        self.bot = bot
        self.append = " `:^)`"

    async def msg(self, ctx, message):
        await ctx.send(message + self.append)

    # ace
    @commands.command(hidden=True)
    @bot.checks.is_member(155625382748356608)
    async def ace(self, ctx):
        await self.msg(ctx, "nabei look what look")

    # akey
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(474170410213048331)
    async def akey(self, ctx):
        if ctx.author.display_name != "ASIAN":
            await ctx.author.edit(nick="ASIAN")

            await self.msg(ctx, ":white_check_mark: Successfully changed this "
                           "Asian's name")
        else:
            await self.msg(ctx, ":x: No need to change this Asian's name" +
                           self.append)

    # archy
    @commands.command(hidden=True)
    @bot.checks.is_member(205107664533848065)
    async def archy(self, ctx):
        options = [
            f"{ctx.author.mention} is a lesbian",
            PACER_TEST
        ]
        option = random.choice(options)

        await self.msg(ctx, option)

    # astaris
    @commands.command(hidden=True)
    @bot.checks.is_member(192974987513036800)
    async def astaris(self, ctx):
        options = [
            "Astaris is big bolly today",
            "Astaris isn't a big bolly today"
        ]
        option = random.choice(options)

        await self.msg(ctx, option)

    # azey
    @commands.command(hidden=True)
    @bot.checks.is_member(239276819918880769)
    async def azey(self, ctx):
        options = [
            "Yes I’m aze pls don’t touch",
            "Archy abuses me"
        ]
        option = random.choice(options)

        await self.msg(ctx, option)

    # beem
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(336336895711772693)
    async def beem(self, ctx):
        if ctx.author.display_name != "Baam":
            await ctx.author.edit(nick="Baam")

            await self.msg(ctx, "Changed stupid Baam's name")
        else:
            await self.msg(ctx, "No need to change stupid Baam's name" +
                           self.append)

    # cat
    @commands.command(hidden=True)
    @bot.checks.is_member(440802535301709827)
    async def cat(self, ctx):
        options = [
            "meow",
            "wat",
            "noni",
            "send help"
        ]
        option = random.choice(options)

        await self.msg(ctx, option)

    # catsis
    @commands.command(hidden=True)
    @bot.checks.is_member(440802535301709827)
    async def catsis(self, ctx):
        options = [
            "You got no jams",
            "Infires",
            "Jjang jjang man bbong bbong",
            "Kkaepjang",
        ]
        option = random.choice(options)

        await self.msg(ctx, option)

    # char
    @commands.command(hidden=True)
    @bot.checks.is_member(473457198207467522)
    async def char(self, ctx):
        await self.msg(ctx, "Char is a lolicon")

    # chun
    @commands.command(hidden=True)
    @bot.checks.is_member(202373732067442690)
    async def chun(self, ctx):
        await self.msg(ctx, "2D girls are better than 3D")

    # fcb
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(283204260781490176)
    async def fcb(self, ctx):
        if ctx.author.display_name != ctx.author.name:
            try:
                await ctx.author.edit(nick=None)
            except discord.errors.Forbidden:
                pass

        await self.msg(ctx, "FCB is h0t")

    # hunter
    @commands.command(hidden=True)
    @bot.checks.is_member(285908956570976259)
    async def hunter(self, ctx):
        await self.msg(ctx, "hunter is gay lol")

    # jackie
    @commands.command(hidden=True)
    @bot.checks.is_member(293025979880833024)
    async def jackie(self, ctx):
        options = [
            "Handsome as **FUCK!**",
            "Jackie is {:,} pounds today."
        ]
        rint = random.randint
        weight = round(rint(1, 100) * rint(1, 100) / (rint(1, 100) /
                       rint(1, 100)), 2)
        option = random.choice(options).format(weight)

        await self.msg(ctx, option)

    # kroy
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(346115225625296897)
    async def kroy(self, ctx):
        if ctx.author.display_name != ctx.author.name:
            try:
                await ctx.author.edit(nick=ctx.author.name)
            except discord.errors.Forbidden:
                pass

            await self.msg(ctx, "Changed Kroyburger's name")
        else:
            await self.msg(ctx, "No need to change Kroyburger's name")

    # menmis
    @commands.command(hidden=True)
    @bot.checks.is_member(286573603368206347)
    async def menmis(self, ctx):
        options = [
            "Menmis is a good mod",
            "Menmis is getting demoted"
        ]
        option = random.choice(options)

        await self.msg(ctx, option + "")

    # orcles
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(301638410815406081)
    async def orcles(self, ctx):
        if ctx.author.display_name != ctx.author.name:
            await ctx.author.edit(nick=None)

            await self.msg(ctx, "Changed obnoxious Orcles's stupid name" +
                           self.append)
        else:
            await self.msg(ctx, "Can't ~~ stand ~~ change Orcles's name." +
                           self.append)

    # Rage
    @commands.command(hidden=True)
    @bot.checks.is_member(447187805106339864)
    async def Rage(self, ctx):
        await self.msg(ctx, "Rage dies faster than light")

    # rory
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(353180156883632128)
    async def rory(self, ctx):
        options = [
            "rory",
            "dinorory rex"
        ]
        option = random.choice(options)

        if ctx.author.display_name != option:
            await ctx.author.edit(nick=option)

            await self.msg(ctx, f":white_check_mark: Successfully changed fat "
                           f"rory's name to \"**{option}**\"")
        else:
            await self.msg(ctx, f":x: No need to change fat rory's name to "
                           f"\"**{option}**\"")

    # sharky
    # sh4rky
    @commands.command(hidden=True)
    @bot.checks.is_member(254759884367724554)
    async def sh4rky(self, ctx):
        await self.msg(ctx, "Below gay")

    # traf
    @commands.command(hidden=True)
    @bot.checks.is_member(311514087639089162)
    async def traf(self, ctx):
        options = [
            "**TRAF IS A MONKEY** :monkey_face::monkey::banana: ooh ooh ooh "
            "ah ah ah!!",
            "**TRAF IS THE OPEST**"
        ]
        option = random.choice(options)

        await self.msg(ctx, option + "")

    # xero
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(257239037721444353)
    async def xero(self, ctx):
        if ctx.author.display_name != ctx.author.name:
            await ctx.author.edit(nick=None)

            await self.msg(ctx, "Changed noob Xero's name")
        else:
            await self.msg(ctx, "No need to change *this* loser's name" +
                           self.append)

    # zogic
    @commands.command(hidden=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @bot.checks.is_member(397628415085379584)
    async def zogic(self, ctx):
        await ctx.author.edit(nick=None)

        await self.msg(ctx, "Don't call me zoggy")


def setup(bot):
    bot.add_cog(Personal(bot))
