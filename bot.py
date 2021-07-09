# Main file for operations
import discord
from discord.ext import commands, tasks
import discord.ext.commands.core

from itertools import cycle

import json
import os

file=open("token.txt","r")

print("Retrieving Token...")
token = file.readline()
token = token[8:]

file.close()
print("Success!")

status = cycle(['Eating children', 'i need 45k/hr mudda bich', 'dn', 'du ma may'])

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        for cog in mapping:
            await self.get_destination().send(f'{cog.qualified_name}: \n\t{[command.name for command in mapping[cog]]}')

    async def send_cog_help(self, cog):
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')

    async def send_group_help(self, group):
        await self.get_destination().send(f'{group.name}: {[command.name for index, command in enumerate(group.commands)]}')

    async def send_command_help(self, command):
        await self.get_destination().send(command.name)

# ----- PREFIXES -----

def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

# This is the command prefix for users to interact with the bot
client = commands.Bot(
    command_prefix = (get_prefix), 
    description = 'basic moderation bot',
    owner_id = '357666029469696000',
    help_command = commands.MinimalHelpCommand(), 
    intents = intents
    )

# Triggers when the bot joins a server
@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = 't.'
    
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

# Triggers when the bot leaves the server
@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))
    
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

# Allows users with administrator perms to change the server's prefix
@client.command()
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix
    
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f"{ctx.author.mention} The server's prefix has successfully changed to {prefix}")

@changeprefix.error
async def changeprefix_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            colour = discord.Colour.red()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.add_field(name='Error: Missing Required Argument(s)', value='Please specify a character to change the server prefix.')

        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title = '`changeprefix` | Missing Required Permissions',
            description = 'You are missing the following permissions: \n```• Administrator```',
            colour = discord.Colour.red()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/749779300181606411/799902760837316628/tumblr_01a3fd42036dbeac4d74baff3a2497ff_ecd049b3_500.gif')

        await ctx.send(embed=embed)

# ----- EVENTS -----
# Sends a message to the terminal that indicates the bot is online and ready to be used
@client.event
async def on_ready():
    change_status.start()
    print('Logged in as {0.user}'.format(client))

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

# Triggers when a user uses an invalid command
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            colour = discord.Colour.red()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.add_field(name='Error', value='This command does not exist')

        await ctx.send(embed=embed)

# Sends the message below if someone joins the server
@client.event
async def on_member_join(member):
    print(f'{member} has joined the server | ')

# Sends the message below if someone leaves the server
@client.event
async def on_member_remove( member):
    print(f'{member} has left the server | ')

# ----- COGS -----

# Checks if the user is the bot owner
def bot_owner(ctx):
        return ctx.author.id == 357666029469696000

# Loads cog
@client.command()
@commands.check(bot_owner)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'The cog: {extension}.py, has been loaded!')

# Unloads cog
@client.command()
@commands.check(bot_owner)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'The cog: {extension}.py, has been unloaded!')

# Reloads cog
@client.command()
@commands.check(bot_owner)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'The cog: {extension}.py, has been reloaded!')

@load.error
@unload.error
@reload.error
async def botOwner_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            description = '**Only bot devs can use this command!**',
            colour = discord.Colour.red()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

        await ctx.send(embed=embed)

# Retrieves only the name from a .py file
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

# Client token
client.run(token)
