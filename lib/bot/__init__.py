from asyncio import sleep
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions
from discord.errors import HTTPException, Forbidden
from discord import Intents
from discord.ext.commands.errors import CommandOnCooldown, MissingPermissions

from ..db import db

OWNER_IDS = [357666029469696000]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"    {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        intents = Intents.all()
        intents.members = True

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=intents
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"    {cog} cog loaded")

        print("setup complete")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)", ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (ID, UserID, GuildID) VALUES (?, ?, ?)", ((hex(member.id + member.guild.id), member.id, member.guild.id) for guild in self.guilds for member in guild.members if not member.bot))

        db.commit()

    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

    async def on_connect(self):
        print("bot is connected")

    async def on_disconnect(self):
        print("bot is disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")
        
        await self.stdout.send("An error occured.")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")

        elif isinstance(exc, MissingPermissions):
            await ctx.send("You don't have the required permissions to run this command!")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"That command is on {'server' if str(exc.cooldown.type).split('.')[-1] == 'guild' else str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} seconds.")

        elif hasattr(exc, "original"):

            if isinstance(exc.original, Forbidden):
                await ctx.send("I don't have permission to do that.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.stdout = self.get_channel(727953882495320184)
            self.scheduler.start()

            self.update_db()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Now online!")
            self.ready = True
            print("bot is ready")

            meta = self.get_cog("Meta")
            await meta.set()

        else:
            print("bot is reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()


