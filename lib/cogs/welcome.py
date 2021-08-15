from discord import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command

from ..db import db

class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (ID, UserID, GuildID) VALUES (?, ?, ?)", hex(member.id+member.guild.id), member.id, member.guild.id)

        wel = list(db.record("SELECT WelcomeChannel FROM guilds WHERE GuildID = ?", member.guild.id))

        if wel[0] == 0:
            pass
        else:
            await self.bot.get_channel(wel[0]).send(f"Welcome to **{member.guild.name}** {member.mention}!")
        
        try:
            await member.send(f"Welcome to **{member.guild.name}**! Please enjoy your stay!")

        except Forbidden:
            pass

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE ID = ?", hex(member.id + member.guild.id))

        wel = list(db.record("SELECT WelcomeChannel FROM guilds WHERE GuildID = ?", member.guild.id))

        if wel[0] == 0:
            pass
        else:
            await self.bot.get_channel(wel[0]).send(f"{member.display_name} has left {member.guild.name}.")

    @Cog.listener()
    async def on_guild_join(self, guild): # Fix these two listeners
        db.execute("INSERT INTO guilds (GuildID) VALUES (?)", guild.id)

        db.multiexec("INSERT INTO exp (ID, UserID, GuildID) VALUES (?, ?, ?)", ((hex(member.id + member.guild.id), member.id, member.guild.id) for member in guild.members if not member.bot))

    @Cog.listener()
    async def on_guild_remove(self, guild):
        db.execute("DELETE FROM guilds WHERE GuildID = ?", guild.id)

        db.multiexec("DELETE FROM exp WHERE ID = ? AND UserID = ? AND GuildID = ?", ((hex(member.id + member.guild.id), member.id, member.guild.id) for member in guild.members if not member.bot))


def setup(bot):
    bot.add_cog(Welcome(bot))