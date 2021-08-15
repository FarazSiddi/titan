from asyncio import sleep

from datetime import datetime, timedelta
from typing import Optional

from discord import Embed, Colour, Member, User
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get

from ..db import db


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data, target):
        self.ctx = ctx
        self.target = target

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(
            title=f"Warnings List of {self.target.display_name}",
            colour=Colour.random()
            )

        embed.set_thumbnail(url=self.target.avatar_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} warnings.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline = False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page*self.per_page) + 1

        fields = []
        table = ("\n".join(f"**{idx+offset}.** WarnID: `{entry[0]}`| Action by `{self.ctx.guild.get_member(entry[4]).name}#{self.ctx.guild.get_member(entry[4]).discriminator}` at `{entry[3]} EST`| Reason: `{entry[5]}` | Policy Violated: `{entry[6]}`" 
                for idx, entry in enumerate(entries)))

        fields.append(("Infractions:", table))

        return await self.write_page(menu, offset, fields)

class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_server_logchannel(self, ctx, guildID): # Fix this command
        pass

    @command(name="kick", brief="MOD: Kicks members out of the server", description="MOD: Kick multiple members out of the server.")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason given"):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position 
                and not target.guild_permissions.administrator):
                    await target.kick(reason=reason)

                    embed = Embed(
                        title="Member kicked",
                        colour=Colour.red(),
                        timestamp=datetime.utcnow()
                    )

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [
                        ("Member", f"`{target.name}` a.k.a. `{target.display_name}` has been kicked", False),
                        ("Action by", f"{ctx.author.name}#{ctx.author.discriminator}", False),
                        ("Reason", reason, False)
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                    if logchannel[0] == 0:
                        await ctx.send(embed=embed)
                    else:
                        await self.bot.get_channel(logchannel[0]).send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} could not be kicked.")
            
            await ctx.send("Action complete")

    @kick_members.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="warn", brief="MOD: Warns members in the server", description="MOD: Warns multiple members in the server. Use if a member/members has violated a rule in your server.")
    @has_permissions(kick_members=True)
    async def warn_members(self, ctx, targets: Greedy[Member], * , reason: Optional[str] = "No reason given"):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            for target in targets:
                if ctx.guild.me.top_role.position > target.top_role.position:
                    polViolated = "False"

                    if reason.lower() == "pol60" or reason.lower() == "pol 60":
                        polViolated = 60

                    elif reason.lower() == "pol61" or reason.lower() == "pol 61":
                        polViolated = 61

                    warnTime = datetime.now()

                    db.execute("INSERT INTO warns (UserID, GuildID, TimeOfViolation, ActionBy, Reason, PolViolated) VALUES (?, ?, ?, ?, ?, ?)", target.id, target.guild.id, 
                    warnTime.strftime("%x") + " " + warnTime.strftime("%X"), ctx.author.id, reason, polViolated)

                    warnsList = db.column("SELECT WarnID FROM warns WHERE UserID = ? AND GuildID = ? ORDER BY WarnID ASC", target.id, target.guild.id)
                    number_of_warns = len(warnsList)

                    warnID = warnsList[number_of_warns-1]

                    embed = Embed(
                    title="Member warned",
                    colour=Colour.red(),
                    timestamp=datetime.utcnow()
                    )

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [
                        ("Member", f"`{target.display_name}` has been warned", False),
                        ("Action by", f"{ctx.author.name}#{ctx.author.discriminator}", False),
                        ("Policy Violated", f"{polViolated}", False),
                        ("Warn Number:", f"{number_of_warns}", False),
                        ("Warn ID:", f"{warnID}", False),
                        ("Reason", reason, False)
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                    if logchannel[0] == 0:
                        await ctx.send(embed=embed)
                    else:
                        await self.bot.get_channel(logchannel[0]).send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} could not be warned.")

            await ctx.send("Action complete")

    @warn_members.error
    async def warn_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="unwarn", brief="MOD: Removes a warn from a member in the server", description="MOD: Removes a warn from a member in the server. Use this command if you give a member a wrong or incorrect warning.")
    @has_permissions(kick_members=True)
    async def unwarn_members(self, ctx, target: Greedy[Member], *, warnID: int):
        if not len(target):
            await ctx.send("One or more required arguments are missing.")

        else:
            for t in target:
                number_of_warns = db.column("SELECT WarnID FROM warns WHERE UserID = ? AND GuildID = ? ORDER BY WarnID ASC", t.id, t.guild.id)
                number_of_warns = len(number_of_warns)+1

                if warnID < 1:
                    await ctx.send("Warn number must be 1 or greater and not less than the highest warning number. Please use 'infr' to check before using this command again.")

                elif ctx.guild.me.top_role.position > t.top_role.position:
                    db.execute("DELETE FROM warns WHERE UserID = ? AND GuildID = ? AND WarnID = ?", t.id, t.guild.id, warnID)

                    embed = Embed(
                        title="Member unwarned",
                        colour=Colour.blue(),
                        timestamp=datetime.utcnow()
                        )

                    embed.set_thumbnail(url=t.avatar_url)

                    fields = [
                        ("Member", t.display_name, False),
                        ("Action by", f"{ctx.author.name}#{ctx.author.discriminator}", False)
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                    if logchannel[0] == 0:
                        await ctx.send(embed=embed)
                    else:
                        await self.bot.get_channel(logchannel[0]).send(embed=embed)

                else:
                    await ctx.send(f"{t.display_name} is not unwarned!")

            await ctx.send("Action complete")

    @unwarn_members.error
    async def unwarn_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="infractions", aliases=["infr"], brief="MOD: Opens a menu where you can view all warns given to a member/s in your server", description="MOD: Opens a menu where you can view all warns given to a member/s in your server. Make sure you use this command first before using the \"t.unwarn\" command.")
    @has_permissions(kick_members=True)
    async def check_infractions(self, ctx, targets: Greedy[Member]):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            for target in targets:
                if ctx.guild.me.top_role.position > target.top_role.position:

                    records = db.records("SELECT * from warns WHERE UserID = ? and GuildID = ? ORDER BY TimeOfViolation ASC", target.id, target.guild.id)

                    menu = MenuPages(source=HelpMenu(ctx, records, target),
                    clear_reactions_after=True,
                    timeout=60.0)

                    await menu.start(ctx)

                else:
                    await ctx.send(f"You cannot check infractions for {target.display_name}.")

    @check_infractions.error
    async def check_infractions_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="ban", brief="MOD: Bans members in the server", description="MOD: Bans multiple members in the server. Use if a member/members has violated a rule or is a repeat offender in your server.")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason given"):
        if not len(targets):
            await ctx.send("One or more required arguments are missing")

        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position 
                and not target.guild_permissions.administrator):
                    await target.ban(reason=reason)

                    embed = Embed(
                        title="Member banned",
                        colour=Colour.red(),
                        timestamp=datetime.utcnow()
                    )

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [
                        ("Member", f"`{target.name}` a.k.a. `{target.display_name}` has been banned", False),
                        ("Action by", f"{ctx.author.name}#{ctx.author.discriminator}", False),
                        ("Reason", reason, False)
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                    if logchannel[0] == 0:
                        await ctx.send(embed=embed)
                    else:
                        await self.bot.get_channel(logchannel[0]).send(embed=embed)

                else:
                    await ctx.send(f"{target.display_name} could not be banned.")

            await ctx.send("Action complete")

    @ban_members.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="unban", brief="MOD: Unbans members in the server", description="MOD: Unbans multiple members in the server. Use if a member/members has appealed their actions and is willing to adhere to your server rules.")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban_members(self, ctx, targets: Greedy[User], *, reason: Optional[str] = "No reason given"):
        if not len(targets):
            await ctx.send("One or more required arguments are missing")

        else:
            for target in targets:

                    banned_users = await ctx.author.guild.bans()

                    embed = Embed(
                        title = f"Member Unbanned",
                        colour = Colour.blue(),
                        timestamp = datetime.utcnow()
                    )

                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [
                        ("Member", f"`{target.name}` a.k.a. `{target.display_name}` has been unbanned", False),
                        ("Action by", f"{ctx.author.name}#{ctx.author.discriminator}", False),
                        ("Reason", reason, False)
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    for ban_entry in banned_users:
                        bannedUser = ban_entry.user

                        if target.id == bannedUser.id or (target.name, target.discriminator) == (bannedUser.name, bannedUser.discriminator):
                            await ctx.guild.unban(target)
                            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                            if logchannel[0] == 0:
                                await ctx.send(embed=embed)
                            else:
                                await self.bot.get_channel(logchannel[0]).send(embed=embed)
                            await ctx.send(f"{target.display_name} has been unbanned.")

            await ctx.send("Action complete")

    @unban_members.error
    async def unban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="clear", aliases=["purge", "delete"], brief="MOD: Deletes a given number of messages sent by users in a channel", description="MOD: Deletes a given number of messages sent by users in a channel. You can also mention members if you want to delete a number of messages sent by specific users.")
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 10):
        def _check(message):
            return not len(targets) or message.author in targets
        
        if 0 < limit <= 250:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit, check=_check)

                await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

        else:
            await ctx.send("The limit provided is not within acceptable bounds. Please enter an amount lower than 250.")

    @command(name="mute", brief="MOD: Mutes members in the server", description="MOD: Mutes multiple members in the server. Use if a member/members has violated a rule in your server.")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_members(self, ctx, targets: Greedy[Member], minutes: Optional[int], *, reason: Optional[str] = "No reason given."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            unmutes = []
            guild = ctx.guild
            mute_role = get(guild.roles, name='muted')

            if not mute_role:
                mute_role = await guild.create_role(name='muted')

                for channel in guild.channels:
                    await channel.set_permissions(mute_role, view_channels=True, speak=False, send_messages=False, read_message_history=True, read_messages=True)

            else:
                for target in targets:
                    if not mute_role in target.roles:
                        if guild.me.top_role.position > target.top_role.position:
                            end_time = datetime.utcnow() + timedelta(seconds=minutes*60) if minutes else None

                            db.execute("INSERT INTO mutes VALUES (?, ?, ?)", target.id, guild.id, 
                            getattr(end_time, "isoformat", lambda: None)())

                            await target.edit(roles=[mute_role])

                            embed = Embed(
                            title="Member muted",
                            colour=Colour.red(),
                            timestamp=datetime.utcnow()
                            )

                            embed.set_thumbnail(url=target.avatar_url)

                            fields = [
                                ("Member", f"`{target.display_name}` has been muted", False),
                                ("Action by", f"{ctx.author.name}#{ctx.author.discriminator}", False),
                                ("Duration", f"{minutes:,} minutes" if minutes else "Indefinite", False),
                                ("Reason", reason, False)
                            ]

                            for name, value, inline in fields:
                                embed.add_field(name=name, value=value, inline=inline)

                            logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                            if logchannel[0] == 0:
                                await ctx.send(embed=embed)
                            else:
                                await self.bot.get_channel(logchannel[0]).send(embed=embed)

                            if minutes:
                                unmutes.append(target)

                        else:
                            await ctx.send(f"{target.display_name} could not be muted.")

                    else:
                        await ctx.send(f"{target.display_name} is already muted!")
                
                    await ctx.send("Action complete")

                    if len(unmutes):
                        await sleep(minutes*60)
                        await self.unmute(ctx, targets)

    @mute_members.error
    async def mute_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    async def unmute(self, ctx, targets, *, reason="Mute time expired."):
        mute_role = get(ctx.guild.roles, name='muted')

        for target in targets:
            if mute_role in target.roles:
                db.execute("DELETE FROM mutes WHERE UserID = ? AND GuildID = ?", target.id, ctx.guild.id)

                await target.remove_roles(mute_role)

                embed = Embed(
                    title="Member unmuted",
                    colour=Colour.red(),
                    timestamp=datetime.utcnow()
                    )

                embed.set_thumbnail(url=target.avatar_url)

                fields = [
                    ("Member", target.display_name, False),
                    ("Reason", reason, False)
                ]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                logchannel = list(db.record("SELECT LogChannel FROM guilds WHERE GuildID = ?", target.guild.id))
                if logchannel[0] == 0:
                    await ctx.send(embed=embed)
                else:
                    await self.bot.get_channel(logchannel[0]).send(embed=embed)

            else:
                await ctx.send(f"{target.display_name} is not muted!")

    @command(name="unmute", brief="MOD: Unmutes members in the server", description="MOD: Unmutes multiple members in the server.")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def unmute_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason given."):
        if not len(targets):
            await ctx.send("One or more required arguments are missing.")

        else:
            await self.unmute(ctx, targets, reason=reason)
            await ctx.send("Action complete")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(864575300981096488)

            self.bot.cogs_ready.ready_up("moderation")

def setup(bot):
    bot.add_cog(Moderation(bot))
