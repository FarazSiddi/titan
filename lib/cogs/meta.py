from apscheduler.triggers.cron import CronTrigger
from time import time
from datetime import datetime, timedelta
from psutil import Process, virtual_memory
from platform import python_version

from discord import Activity, ActivityType, Embed, Colour
from discord import __version__ as discord_version
from discord.ext.commands import Cog
from discord.ext.commands import command

from ..db import db

class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "watching +help | {users:,} users in {guilds:,} servers"

        bot.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def message(self):
        return self._message.format(users=len(self.bot.users), guilds=len(self.bot.guilds))

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type.")

        self._message = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.bot.change_presence(activity=Activity(
            name=_name,
            type=getattr(ActivityType, _type, ActivityType.playing)
        ))

    @command(name="setactivity", brief="OWNER/DEV: Change's the bot's current activity displayed", hidden=True)
    async def set_activity_message(self, ctx, *, text: str):
        if ctx.author.id == self.bot.owner_ids[0]:
            self.message = text
            await self.set()

        else:
            await ctx.send(f"You don't have permission to use this command {ctx.author.mention}!")

    @command(name="ping", brief="Displays the bot's latency and response time", description="Displays the bot's latency and response time.")
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(f"Pong! DWSP latency: {self.bot.latency*1000:,.0f} ms.")
        end = time()

        await message.edit(content=f"Pong! DWSP latency: {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms.")

    @command(name="stats", brief="Displays the bot's current stats", description="Display's the bot's current stats such as bot uptime, memory used, Python and discord.py version, etc.")
    async def show_bot_stats(self, ctx):
        embed = Embed(
            title="Bot stats",
            colour=Colour.random(),
            thumbnail=self.bot.user.avatar_url,
            timestamp=datetime.utcnow()
        )

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time()-proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024**2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("Bot version", self.bot.VERSION, True),
            ("Python version", python_version(), True),
            ("discord.py version", discord_version, True),
            ("Uptime", uptime, True),
            ("CPU time", cpu_time, True),
            ("Memory usage", f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:,.2f}%)", True),
            ("Users", f"{len(self.bot.users):,}", True),
            ("Guilds", f"{len(self.bot.guilds):,}", True)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name="shutdown", brief="OWNER/DEV: Shuts down the bot", hidden=True)
    async def shutdown(self, ctx):
        if ctx.author.id == self.bot.owner_ids[0]:
            await ctx.send("Shutting down...")

            db.commit()
            self.bot.scheduler.shutdown()
            await self.bot.logout()

        else:
            await ctx.send(f"You don't have permission to use this command {ctx.author.mention}!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("meta")

def setup(bot):
    bot.add_cog(Meta(bot))