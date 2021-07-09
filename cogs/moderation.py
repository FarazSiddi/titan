import discord
from discord.ext import commands

import random
import asyncio
import datetime

insults = ['retard', 'dumbass', 'dipshit', 'mudda bitch', 'stoopid']
multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'mo': 2592000, 'y': 31536000}

class DurationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        amount = argument[:-1]
        unit = argument[-1]

        if amount.isdigit() and unit in ['s', 'm', 'h', 'd', 'w', 'mo', 'y']:
            return (int(amount), unit)

        raise commands.BadArgument(message='Not a valid duration')

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client
    
# Users who have the "Manage Messages" permission can delete messages using this command
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=amount + 1)

        embed = discord.Embed(
            title = f"{amount} messages have been removed!",
            colour = discord.Colour.blue()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

        await ctx.send(embed=embed, delete_after=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`clear` | Missing Required Arguments',
                description = f'```Please specify an amount of messages to delete {insults[random.randint(0, len(insults)-1)]}.```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/655436762751041587.png?v=1')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`clear` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Manage Messages```',
                colour = discord.Colour.red()
            )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

        await ctx.send(embed=embed)

# Users who have the "Manage Messages" permission can mute non-moderator members using this command <----- TO BE COMPLETED
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def mute(self, ctx, member : commands.MemberConverter, duration: DurationConverter, *, reason="None"):
                        
        amount, unit = duration

        embed = discord.Embed(
            title = f"***:white_check_mark:  {member.name}#{member.discriminator} has been muted for {amount}{unit}! | Reason: {reason}***",
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed2 = discord.Embed(
            title = f'***You were muted in  `{ctx.guild.name}`  for {amount}{unit}! | Reason: {reason}***',
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name='muted')

        if not mutedRole:
            mutedRole = await guild.create_role(name='muted')

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, view_channels=True, speak=False, send_messages=False, read_message_history=True, read_messages=True)

        await ctx.send(embed=embed)
        await member.send(embed=embed2)
        await member.add_roles(mutedRole)
        await asyncio.sleep(amount * multiplier[unit])
        await member.remove_roles(mutedRole)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`mute` | Missing Required Arguments',
                description = f'```Who do you want to mute {insults[random.randint(0, len(insults)-1)]}?\nAnd for how long?```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/655436762751041587.png?v=1')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`mute` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Manage Messages```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title = '`mute` | Member Not Found',
                description = "```Incorrect input or this user doesn't exist in this server```",
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/690958886819201056.gif?v=1')

            await ctx.send(embed=embed)

# Users who have the "Manage Messages" permission can unmute non-moderator members using this command <----- TO BE COMPLETED
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def unmute(self, ctx, member : discord.Member):
        mutedRole = discord.utils.get(ctx.guild.roles, name='muted')

        embed = discord.Embed(
            title = f"***:white_check_mark:  Unmuted {member.name}#{member.discriminator}***",
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed2 = discord.Embed(
            title = f'***You were unmuted in the server  `{ctx.guild.name}` ***',
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')


        await member.remove_roles(mutedRole)
        await ctx.send(embed=embed)
        await member.send(embed=embed2)

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`unmute` | Missing Required Arguments',
                description = f'```Who do you want to unmute {insults[random.randint(0, len(insults)-1)]}?```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/655436762751041587.png?v=1')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`unmute` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Manage Messages```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title = '`unmute` | Member Not Found',
                description = "```Incorrect input or this user doesn't exist in this server```",
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/690958886819201056.gif?v=1')

            await ctx.send(embed=embed)

# Users who have the "Kick Members" permission can kick other members using this basic command
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member, *, reason="None"):

        embed = discord.Embed(
            title = f"***:white_check_mark:  {member.name}#{member.discriminator} has been kicked! | Reason: {reason}***",
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed2 = discord.Embed(
            title = f'***You were kicked from the server  `{ctx.guild.name}` ! | Reason: {reason}***',
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

        await member.send(embed=embed2)
        await ctx.send(embed=embed)
        await member.kick(reason=reason)
    
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`kick` | Missing Required Arguments',
                description = f'```Who do you want to kick {insults[random.randint(0, len(insults)-1)]}?```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/655436762751041587.png?v=1')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`kick` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Kick Members```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title = '`kick` | Member Not Found',
                description = "```Incorrect input or this user doesn't exist in this server```",
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/690958886819201056.gif?v=1')

            await ctx.send(embed=embed)


# Users who have the "Ban Members" permission can ban other members using this basic command
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member : commands.MemberConverter, duration: DurationConverter, *, reason="None"):
        
        amount, unit = duration

        embed = discord.Embed(
            title = f"***:white_check_mark:  {member.name}#{member.discriminator} has been banned for {amount}{unit}! Reason: {reason}***",
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed2 = discord.Embed(
            title = f'***You were banned in the server  `{ctx.guild.name}`  for {amount}{unit} | Reason: {reason}***',
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

        await member.send(embed=embed2)
        await ctx.send(embed=embed)
        await ctx.guild.ban(member, reason=reason)
        await asyncio.sleep(amount * multiplier[unit])
        await ctx.guild.unban(member)
    
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`ban` | Missing Required Arguments',
                description = f'```Who do you want to ban {insults[random.randint(0, len(insults)-1)]}?\nAnd for how long?```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/655436762751041587.png?v=1')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`ban` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Ban Members```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(
                title = '`ban` | Member Not Found',
                description = "```Incorrect input or this user doesn't exist in this server```",
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/690958886819201056.gif?v=1')

            await ctx.send(embed=embed)
        
# Users who have the "Ban Members" permission can unban other members using this basic command
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, *, user : commands.UserConverter):
        banned_users = await ctx.guild.bans()

        embed = discord.Embed(
            title = f"***:white_check_mark:  {user.name}#{user.discriminator} is now unbanned!***",
            colour = discord.Colour.blue(),
            timestamp = datetime.datetime.utcnow()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

        for ban_entry in banned_users:
            bannedUser = ban_entry.user

            if user.id == bannedUser.id or (user.name, user.discriminator) == (bannedUser.name, bannedUser.discriminator):
                await ctx.guild.unban(user)
                await ctx.send(embed=embed)
                return

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`unban` | Missing Required Arguments',
                description = f'```Who do you want to unban {insults[random.randint(0, len(insults)-1)]}?```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/655436762751041587.png?v=1')

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title = '`unban` | Missing Required Permissions',
                description = 'You are missing the following permissions: \n```• Ban Members```',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Moderation(client))