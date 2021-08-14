from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions, bot_has_permissions

from discord import TextChannel, Colour, Embed
from discord.utils import get

from datetime import datetime

from ..db import db

class Presets(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("presets")

    @command(name="assign", aliases=["assignChannel", "ac"], brief="ADMIN/SERVER OWNER: Assigns a given channel into either a log(logs)/lvl(level-up)/wel(welcome)/sb(starboard) channel operated by the bot") # Fix this command
    @has_permissions(manage_channels=True)
    async def assign_channel(self, ctx, _channel: TextChannel, channelType):
        if not len(channelType):
            await ctx.send("One or more required arguments are missing.")

        else:

            if channelType.lower() == "log":
                db.execute("UPDATE guilds SET LogChannel = ? WHERE GuildID = ?", _channel.id, ctx.author.guild.id)
            elif channelType.lower() == "lvl":
                db.execute("UPDATE guilds SET LevelUpChannel = ? WHERE GuildID = ?", _channel.id, ctx.author.guild.id)
            elif channelType.lower() == "wel":
                db.execute("UPDATE guilds SET WelcomeChannel = ? WHERE GuildID = ?", _channel.id, ctx.author.guild.id)
            elif channelType.lower() == "sb":
                db.execute("UPDATE guilds SET StarboardChannel = ? WHERE GuildID = ?", _channel.id, ctx.author.guild.id)
            else:
                await ctx.send("Please specify the correct channel type you want to assign. The options are: log/lvl/wel/sb.")

            await ctx.send("Action complete")

    @command(name="viewAssignedChannels", aliases=["viewAssigned", "vac"], brief="ADMIN/SERVER OWNER: Views all channels that are specially assigned to the bot.") # Fix this command
    @has_permissions(manage_channels=True)
    async def view_assigned_channels(self, ctx):
        records = db.record("SELECT * from guilds WHERE GuildID = ?", ctx.guild.id)

        embed = Embed(
            title=f"Assigned channels for `{ctx.author.guild}`",
            colour=Colour.random(),
            timestamp=datetime.utcnow()
        )

        fields = [
            ("Log Channel", f"{self.bot.get_channel(records[2])}", False),
            ("Starboard Channel", f"{self.bot.get_channel(records[3])}", False),
            ("Level Up Channel", f"{self.bot.get_channel(records[4])}", False),
            ("Welcome Channel", f"{self.bot.get_channel(records[5])}", False)

        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name="unassign", aliases=["unassignChannel", "uac"], brief="ADMIN/SERVER OWNER: Unassigns a given channel that is specially operated by the bot.", description="ADMIN/SERVER OWNER: Unassigns a given channel that is specially operated by the bot. The options are log(logs)/lvl(level-up)/wel(welcome)/sb(starboard).") # Fix this command
    @has_permissions(manage_channels=True)
    async def unassign_channel(self, ctx, channelType):
        if not len(channelType):
            await ctx.send("One or more required arguments are missing.")

        else:

            if channelType.lower() == "log":
                db.execute("UPDATE guilds SET LogChannel = 0 WHERE GuildID = ?", ctx.author.guild.id)
            elif channelType.lower() == "lvl":
                db.execute("UPDATE guilds SET LevelUpChannel = 0 WHERE GuildID = ?", ctx.author.guild.id)
            elif channelType.lower() == "wel":
                db.execute("UPDATE guilds SET WelcomeChannel = 0 WHERE GuildID = ?", ctx.author.guild.id)
            elif channelType.lower() == "sb":
                db.execute("UPDATE guilds SET StarboardChannel = 0 WHERE GuildID = ?", ctx.author.guild.id)
            else:
                await ctx.send("Please specify the correct channel type you want to unassign. The options are: log(logs)/lvl(level-up)/wel(welcome)/sb(starboard).")

            await ctx.send("Action complete")

def setup(bot):
    bot.add_cog(Presets(bot))