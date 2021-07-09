import discord
from discord.ext import commands
from discord.ext.commands import Cog

import random
import asyncio
import datetime

def convert(argument):
    
    pos = ['s', 'm', 'h', 'd', 'w', 'mo', 'y']

    unit = argument[-1]

    multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'mo': 2592000, 'y': 31536000}

    if unit not in pos:
        return -1

    try:
        val = int(argument[:-1])
    except:
        return -2

    return val * multiplier[unit]

class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.polls = []

    # Members with a specialized role can start a giveaway using this command below <--- Will add an option where one can choose the number of winners [COMING SOON]
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def giveaway(self, ctx):
        await ctx.send("Creating Giveaway... Answer these questions within 15 seconds.")

        questions = [
            "Which channel should it be hosted in?",
            "What should be the duration of the giveaway? (use s/m/h/d/w/mo/y for reference)",
            "What is the prize of the giveaway?"
        ]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.client.wait_for('message', timeout = 15.0, check = check)

            except asyncio.TimeoutError:
                await ctx.send("You didn't answer the question in time, please try again.")
                return

            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])

        except:
            await ctx.send(f"You didn't mention the channel properly. Do it like this: {ctx.channel.mention}")
            return

        channel = self.client.get_channel(c_id)

        time = convert(answers[1])

        if time == -1:
            await ctx.send("You didn't answer the time with a proper unit. Use (s/m/h/d/w/mo/y).")
            return

        elif time == -2:
            await ctx.send("The time must be an integer. Please enter an integer next time.")
            return

        prize = answers[2]

        await ctx.send(f"The giveaway will be in {channel.mention} and will last {answers[1]}")

        embed = discord.Embed(
            title = "Giveaway!",
            description = f"{prize}",
            colour = discord.Colour.random(),
            timestamp = datetime.datetime.utcnow()
        )

        embed.add_field(name = f'Hosted by:', value = ctx.author.mention)
        embed.set_footer(text = f"Ends {answers[1]} from now!")

        my_msg = await channel.send(embed=embed)

        await my_msg.add_reaction("🎉")

        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await channel.send(f"Congratulations! {winner.mention} won {prize}!")
    
    # Members with a specialized role can reroll a giveaway using this command below (For example: .reroll #bot-spam 861117533292462081)
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def reroll(self, ctx, channel : discord.TextChannel, id_ : int):
        try:
            new_msg = await channel.fetch_message(id_)
        except:
            await ctx.send('The id was entered incorrectly')
            return

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await channel.send(f"Congratulations! The new winner is {winner.mention}.")

    # Raises errors for the .giveaway and .reroll commands
    @giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`giveaway` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Ban Users```',
                colour = discord.Colour.red()
            )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

        await ctx.send(embed=embed)

    @reroll.error
    async def reroll_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`reroll` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Ban Users```',
                colour = discord.Colour.red()
            )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

        await ctx.send(embed=embed)

    # Members with a specialized role can use this command to create a poll
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def poll(self, ctx):
        await ctx.send("Creating poll... Answer these questions within 15 seconds.")

        questions = [
            "Which channel should it be hosted in?",
            "What should the name of the poll be?",
            "What should be the duration of the poll? (use s/m/h/d/w/mo/y for reference)",
            "How many choices do you want to put in this poll? `(Note: Minimum amount of choices is 2 and the maximum amount allowed is 9)`"
        ]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.client.wait_for('message', timeout = 15.0, check = check)

            except asyncio.TimeoutError:
                await ctx.send("You didn't answer the question in time, please try again!")
                return

            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])

        except:
            await ctx.send(f"You didn't mention the channel properly! Do it like this: {ctx.channel.mention}")
            return

        pollTitle = answers[1]

        channel = self.client.get_channel(c_id)

        time = convert(answers[2])

        if time == -1:
            await ctx.send("You didn't answer the time with a proper unit. Use (s/m/h/d/w/mo/y).")
            return

        elif time == -2:
            await ctx.send("The time must be an integer. Please enter an integer next time.")
            return

        choice_num = int(answers[3])

        if choice_num > 9 or choice_num < 2:
            await ctx.send("The number must be in a range between 2 to 9!")
            return

        choices = []

        for j in range(choice_num):

            try:
                await ctx.send(f'Choice #{j+1}:')
                choice = await self.client.wait_for('message', timeout = 15.0, check = check)

            except asyncio.TimeoutError:
                await ctx.send("You didn't answer the question in time, please try again!")
                return

            else:
                choices.append(choice.content)

        emotes = ['🔴', '🔵', '🟡', '🟢', '🟣', '🟠', '🟤', '⚪', '⚫']

        await ctx.send(f"The poll will be in {channel.mention} and will last for {answers[2]}")

        embed = discord.Embed(
            title = "Poll",
            description = f"{pollTitle}",
            colour = discord.Colour.random(),
            timestamp = datetime.datetime.utcnow()
        )

        fields = [("Options", '\n'.join([f"{emotes[k]} {choices[k]}" for k in range(choice_num)]), False), ("Instructions", "React to cast a vote!", False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text = f"Ends {answers[2]} from now!")

        message = await channel.send(embed=embed)

        for l in range(choice_num):
            await message.add_reaction(emotes[l])

        self.polls.append((message.channel.id, message.id))

        self.client.scheduler.add_job(self.complete_poll, "date", run_date=datetime.datetime.now()+datetime.timedelta(seconds=time), args=[message.channel.id, message.id])

    async def complete_poll(self, channel_id, message_id):
        message = await self.client.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!")
        self.polls.remove((message.channel.id, message.id))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.message_id in (poll[1] for poll in self.polls):
            message = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                and payload.member in await reaction.users().flatten()
                and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)       

    # Members with a specialized role can use this command to create an automatic role assignment prompt
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def auto_assign_roles(self, ctx):
        pass

def setup(client):
    client.add_cog(Misc(client))