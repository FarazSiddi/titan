# titan (v0.1.1)
Titan is a discord bot made by null#8672 on discord (null-2020 on GitHub)

This is my first ever python project that is uploaded to the GitHub repository, and will be one of the few projects that I will actively update.

Titan is intended to be a basic moderation bot with a few more interesting commands that will stand out, and is also showcased as a culmination
of my knowledge of the python syntax and its libraries.

More information will be added as time and more ideas will be implemented.

Thank you.

Updates (v0.1.1):
- Added 3 new commands for the bot developers and owner to use: t.lcog (loads cog), t.uncog (unloads cog), and t.recog (reloads cog). 
  This is for making changes to the bot without having to shut it down beforehand, preventing some bot functions from malfunctioning.

- Shortened the name of the cog that holds moderation commands: from "moderation.py" to "mod.py"

Updates (v0.1):
- Revamped the source code of the bot

- Changed and improved the arrangement of files and folders for better code management.

- Added more commands such as t.bonk, t.warn, t.poll, t.starboard, and more.

- Added a serverwide leveling and ranking system.

- New and more refined custom help menu (will tweak it further in future updates).

- Added a log channel where moderators, administrators, and owners can check for member updates and events.

- Introduced a SQL storage system using sqlite3 with Python. This means commands such as t.rank, t.leaderboard, etc. will make use of this system.

- Instead of asyncio, the bot now uses apscheduler to set times for certain commands such as t.giveaway, t.poll, etc.

Expected Updates (v0.2?):
- Load, unload, and reload cogs using discord commands. This is so one can make changes to the bot without having to shut it down beforehand.

- Webscraping websites such as Urban Dictionary, Course pages and program calendars on the Ryerson website (if allowed), Reddit, and more. 

- Adding a math cog to allow users to calculate math problems through numpy, Pandas, seaborne?, and matplotlib.

- Adding new commands for the "fun" cog.

- Fixing and improving existing commands and bugs.