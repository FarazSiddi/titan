from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command

from ..db import db

class Log(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(864575300981096488)
            self.bot.cogs_ready.ready_up("log")

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            embed = Embed(
                title=f"Username change | `{after.display_name}`",
                colour=after.colour,
                timestamp=datetime.utcnow()
            )

            embed.set_thumbnail(url=before.avatar_url)
            
            fields = [("Before", before.name, False), ("After", after.name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", after.guild.id))

            if logchannel[0] == 0:
                pass
            else:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = Embed(
                title=f"Discriminator change | `{after.name}`",
                colour=after.colour,
                timestamp=datetime.utcnow()
            )

            fields = [("Before", before.discriminator, False), ("After", after.discriminator, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            logchannel = db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", after.guild.id)
            if logchannel[0] == 0:
                pass
            else:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(
                title=f"Avatar change | `{after.name}`",
                description="New image is below, old image is on the right",
                colour=after.colour,
                timestamp=datetime.utcnow()
            )
            
            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", after.guild.id))
            if logchannel[0] == 0:
                pass
            else:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)


    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            embed = Embed(
                title=f"Nickname change | `{after.name}`",
                colour=after.colour,
                timestamp=datetime.utcnow()
            )

            embed.set_thumbnail(url=before.avatar_url)
            
            fields = [("Before", before.display_name, False), ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", after.guild.id))
            await self.bot.get_channel(logchannel[0]).send(embed=embed)

        if before.roles != after.roles:
            embed = Embed(
                title=f"Role change | `{after.name}`",
                colour=after.colour,
                timestamp=datetime.utcnow()
            )

            embed.set_thumbnail(url=before.avatar_url)
            
            fields = [("Before", ", ".join([r.mention for r in before.roles]), False), ("After", ", ".join([r.mention for r in after.roles]), False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", after.guild.id))
            if logchannel[0] == 0:
                pass
            else:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)


    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(
                        title=f"Message edited | `{after.author.name}`",
                        colour=after.author.colour,
                        timestamp=datetime.utcnow()
                )

                embed.set_thumbnail(url=before.author.avatar_url)
                
                fields = [("Before", before.content, False), ("After", after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", after.guild.id))
                if logchannel[0] == 0:
                    pass
                else:
                    await self.bot.get_channel(logchannel[0]).send(embed=embed)



    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            embed = Embed(
                    title=f"Message deleted | `{message.author.name}`",
                    colour=message.author.colour,
                    timestamp=datetime.utcnow()
            )

            embed.set_thumbnail(url=message.author.avatar_url)

            embed.add_field(name="Content", value=message.content, inline=False)

            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", message.author.guild.id))
            if logchannel[0] == 0:
                pass
            else:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)

def setup(bot):
    bot.add_cog(Log(bot))