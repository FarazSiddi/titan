from datetime import datetime, timedelta
from discord import Embed, Colour
from random import choice

from ..db import db

from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.polls = []
        self.giveaways = []

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reactions")

            self.starboard_channel = self.bot.get_channel(871600252006830090) # Create starboard_channel function

    @command(name="poll", aliases=["createpoll"], brief="Creates a server-wide poll.", description="Creates a server-wide poll. Please Note: You can use double quotation marks (\"\") around the question and options to bypass the one-word options issue.")
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, minutes: int, question: str, *options):
        if len(options) > 10:
            await ctx.send("You can only create a maximum of 10 options.")

        else:
            embed = Embed(
                title="Poll",
                description=question,
                colour=Colour.random(),
                timestamp=datetime.utcnow()
            )

            fields = [
                ("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                ("Instructions", "React to cast a vote!", False)
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline = inline)

            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)

            self.polls.append((message.channel.id, message.id))

            self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=minutes*60), args=[message.channel.id, message.id])

    @command(name="giveaway", brief="Creates a giveaway poll", description="Creates a giveaway poll.")
    @has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx, mins: int, *, description: str):
        embed = Embed(
            title="Giveaway!",
            description=description,
            colour=Colour.random(),
            timestamp=datetime.utcnow()
        )

        fields = [
            ("End time", f"{datetime.utcnow()+timedelta(seconds=mins*60)} UTC", False),
            ("Instructions", "React to cast a vote!", False)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline = inline)

        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")

        self.giveaways.append((message.channel.id, message.id))

        self.bot.scheduler.add_job(self.complete_giveaway, "date", run_date=datetime.now()+timedelta(seconds=mins*60), args=[message.channel.id, message.id])


    async def complete_giveaway(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        if len((entrants:= [u for u in await message.reactions[0].users().flatten() if not u.bot])) > 0:
            winner = choice(entrants)
            await message.channel.send(f"Congratulations {winner.mention} - you won the giveaway!")
            self.giveaways.remove((message.channel.id, message.id))

        else:
            await message.channel.send("Giveaway ended - no one entered!")
            self.giveaways.remove((message.channel.id, message.id))

    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!")
        self.polls.remove((message.channel.id, message.id))


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                and payload.member in await reaction.users().flatten()
                and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)   

        elif payload.emoji.name == "⭐":
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not message.author.bot and payload.member.id != message.author.id:
                msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?", message.id) or (None, 0)

                embed = Embed(
                    title = "Starred Message",
                    colour = Colour.random(),
                    timestamp = datetime.utcnow()
                )

                fields = [
                    ("Author", message.author.mention, False),
                    ("Content", message.content or "See attachment", False),
                    ("Stars", stars+1, False)
                ]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                if not stars:
                    sb = list(db.record("SELECT StarboardChannel FROM guilds WHERE GuildID = ?", message.author.guild.id))
                    if sb[0] == 0:
                        pass
                    else:
                        star_message = await self.bot.get_channel(sb[0]).send(embed=embed)

                        db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)", message.id, star_message.id)

                else:
                    sb = list(db.record("SELECT StarboardChannel FROM guilds WHERE GuildID = ?", message.author.guild.id))
                    if sb[0] == 0:
                        pass
                    else:
                        star_message = await self.bot.get_channel(sb[0]).fetch_message(msg_id)

                        await star_message.edit(embed=embed)
                        db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)
            
            else:
                await message.remove_reaction(payload.emoji, payload.member)

def setup(bot):
    bot.add_cog(Reactions(bot))
