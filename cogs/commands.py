#import discord
import discord
from discord.ext import commands
import random

class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Sends the message below along with the user's ping if a user were to enter '.ping'
    @commands.command()
    async def ping(self, ctx):
        thumbnails = ['https://cdn.discordapp.com/emojis/836675974917521438.png?v=1',
                    'https://cdn.discordapp.com/emojis/836668443168079962.png?v=1',
                    'https://cdn.discordapp.com/emojis/837388162170355813.png?v=1',
                    'https://cdn.discordapp.com/emojis/836706911453577226.png?v=1',
                    'https://cdn.discordapp.com/emojis/836670068976123915.png?v=1',
                    'https://cdn.discordapp.com/emojis/836674154606493706.png?v=1',
                    'https://cdn.discordapp.com/emojis/814291705754681365.png?v=1']

        embed = discord.Embed(
            title = '`ping`',
            colour = discord.Colour.random()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.set_thumbnail(url=random.choice(thumbnails))
        embed.add_field(name='Pong!', value=f'```{round(self.client.latency * 1000)}ms```')

        await ctx.send(embed=embed)

    # Sends one of the many responses to a user who enters the '.8ball' command along with a question
    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain.',
                    'It is decidedly so.',
                    'Without a doubt.',
                    'Yes - definitely.',
                    'You may rely on it.',
                    'As I see it, yes.',
                    'Most likely.',
                    'Outlook good.',
                    'Yes.',
                    'Signs point to yes.',
                    'Reply hazy, try again.',
                    'Ask again later.',
                    'Better not tell you now.',
                    'Cannot predict now.',
                    'Concentrate and ask again.',
                    "Don't count on it.",
                    'My reply is no.',
                    'My sources say no.',
                    'Outlook not so good.',
                    'Very doubtful.']

        embed = discord.Embed(
            title = '`8ball`',
            colour = discord.Colour.random()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.add_field(name=f'Question: {question}', value=f'Answer: {random.choice(responses)}')

        await ctx.send(embed=embed)

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = '`8ball` | Missing Required Arguments',
                description = 'Ask a question stoopid.',
                colour = discord.Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

            await ctx.send(embed=embed)

# Checks if the user is the bot owner
    def bot_owner(ctx):
        return ctx.author.id == 357666029469696000
    
    @commands.command(aliases=['botOwner'])
    @commands.check(bot_owner)
    async def check_if_bot_owner(self, ctx):
        await ctx.send(f'{ctx.author.mention} You are the owner of this bot!')

    @check_if_bot_owner.error
    async def check_if_bot_owner_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{ctx.author.mention} The owner of this bot is null#8672. Website coming soon!")

def setup(client):
    client.add_cog(Commands(client))