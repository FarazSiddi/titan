from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from discord.ext.menus import MenuPages, ListPageSource

from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Member
from discord import Embed, Colour

from ..db import db

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(
            title="XP Leaderboard",
            colour=Colour.random()
            )

        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} members.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline = False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page*self.per_page) + 1

        fields = []
        table = ("\n".join(f"{idx+offset}. {self.ctx.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Level: {entry[2]})" 
                for idx, entry in enumerate(entries)))

        fields.append(("Ranks", table))

        return await self.write_page(menu, offset, fields)

class Exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE ID = ?", hex(message.author.id + message.author.guild.id))

        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_add = randint(10, 20)

        new_lvl = int(((xp+xp_add)//42) ** 0.55)

        db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE ID = ?", xp_add, new_lvl, (datetime.utcnow()+timedelta(seconds=10)).isoformat(), hex(message.author.id + message.author.guild.id))

        if new_lvl > lvl:
            lvl_channel = list(db.record("SELECT LevelUpChannel FROM guilds WHERE GuildID = ?", message.author.guild.id))

            if lvl_channel[0] is not 0:
                await self.bot.wait_until_ready()
                await self.bot.get_channel(lvl_channel[0]).send(f"Congrats {message.author.mention}! You reached level {new_lvl:,}.")
            
            else:
                await message.channel.send(f"Congrats {message.author.mention}! You reached level {new_lvl:,}.")

    @command(name='level', brief="Displays a user's or the caller's level", description="Displays a user's or the caller's level.")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record("SELECT XP, Level FROM exp WHERE ID = ?", hex(target.id + target.guild.id)) or (None, None)

        if lvl is not None:
            await ctx.send(f"{target.mention} is on level {lvl:,} with {xp:,} XP.")

        else:
            await ctx.send("That member is not tracked by the XP system.")

    @command(name="rank", brief="Displays a user's or the caller's rank within the server", description="Displays a user's or the caller's rank within the server.")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM exp WHERE GuildID = ? ORDER BY XP DESC", target.guild.id)

        try:
            await ctx.send(f"{target.mention} is rank {ids.index(target.id)+1} of {len(ids)}.")

        except ValueError:
            await ctx.send("That member is not tracked by the XP system.")

    @command(name="leaderboard", aliases=["lb"], brief="Displays the server's leaderboard", description="Displays the server's leaderboard.")
    async def display_leaderboard(self, ctx):
        records = db.records("SELECT UserID, XP, Level FROM exp WHERE GuildID = ? ORDER BY XP DESC", ctx.author.guild.id)

        menu = MenuPages(source=HelpMenu(ctx, records),
                        clear_reactions_after=True,
                        timeout=60.0)

        await menu.start(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.levelup_channel = self.bot.get_channel(872167190986637313)

            self.bot.cogs_ready.ready_up("exp")

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message)

def setup(bot):
    bot.add_cog(Exp(bot))