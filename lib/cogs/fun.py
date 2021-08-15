from random import choice, randint
from typing import Optional

from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import BadArgument
from discord import Member, Embed, Colour
from discord.ext.commands.errors import MissingRequiredArgument

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi"], brief="Say hello to the bot", description="Greet Titan with either a \"hi\" or a \"hello\"!")
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")
    
    @command(name="dice", aliases=['roll'], brief="Roles a dice", description="Role a dice or a group of dices with the # of sides you want for all of them. For example, type \"t.dice 2d6\" to roll two dices with 6 sides each.") # t.dice [no. of dice]d[values]
    @cooldown(1, 5, BucketType.user)
    async def roll_dice(self, ctx, die_string: str = "2d6"):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join(str(r) for r in rolls) + f" = {sum(rolls)}")

        else:
            await ctx.send("I can't roll that many dice. Please try a lower number!")

    @command(name="bonk", aliases=["hit"], brief="Bonks horny people", description="Ping a member in the server to bonk them if they get too lewd!")
    async def bonk_member(self, ctx, member: Member, *, reason: Optional[str] = "being too horny"):
        await ctx.send(f"{ctx.author.mention} bonked {member.mention} for {reason}!")

    @bonk_member.error
    async def bonk_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Member not found.")

    @command(name="8ball", brief="Ask a question to the 8ball!", description="Ask a question to the 8ball and it will respond with one of the many possible answers!")
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

        embed = Embed(
            title = '`8ball`',
            colour = Colour.random()
        )

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
        embed.add_field(name=f'Question: {question}', value=f'Answer: {choice(responses)}')

        await ctx.send(embed=embed)

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            embed = Embed(
                title = '`8ball` | Missing Required Arguments',
                description = 'Ask a question stoopid.',
                colour = Colour.red()
            )

            embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

            await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))