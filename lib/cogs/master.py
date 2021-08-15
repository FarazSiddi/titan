from discord.ext.commands import Cog
from discord.ext.commands import command

class Master(Cog):
    def __init__(self, bot):
        self.bot = bot

    # Loads cog
    @command(name="loadCog", aliases=['lcog'], brief="OWNER/DEV: Loads cog (extension) into the bot if cog is already unloaded", hidden=True)
    async def load_cog(self, ctx, extension):
        if ctx.author.id == self.bot.owner_ids[0]:
            self.bot.load_extension(f'lib.cogs.{extension}')
            await ctx.send(f'{extension}.py loaded')
        else:
            await ctx.send(f"You don't have permission to use this command {ctx.author.mention}!")

    # Unloads cog
    @command(name="unloadCog", aliases=['uncog'], brief="OWNER/DEV: Unloads cog (extension) from the bot if cog is already loaded", hidden=True)
    async def unload_cog(self, ctx, extension):
        if ctx.author.id == self.bot.owner_ids[0]:
            self.bot.unload_extension(f'lib.cogs.{extension}')
            await ctx.send(f'{extension}.py unloaded')
        else:
            await ctx.send(f"You don't have permission to use this command {ctx.author.mention}!")

    # Reloads cog
    @command(name="reloadCog", aliases=['recog'], brief="OWNER/DEV: Reloads cog (extension) that is currently installed into the bot if cog is in file", hidden=True)
    async def reload_cog(self, ctx, extension):
        if ctx.author.id == self.bot.owner_ids[0]:
            self.bot.unload_extension(f'lib.cogs.{extension}')
            self.bot.load_extension(f'lib.cogs.{extension}')
            await ctx.send(f'{extension}.py reloaded')
        else:
            await ctx.send(f"You don't have permission to use this command {ctx.author.mention}!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("master")

def setup(bot):
    bot.add_cog(Master(bot))