CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer PRIMARY KEY,
    Prefix text DEFAULT "t.",
    LogChannel integer DEFAULT 0,
    StarboardChannel integer DEFAULT 0,
    LevelUpChannel integer DEFAULT 0,
    WelcomeChannel integer DEFAULT 0
);

CREATE TABLE IF NOT EXISTS exp (
    ID text PRIMARY KEY,
    UserID integer,
    GuildID integer,
    XP integer DEFAULT 0,
    Level integer DEFAULT 0,
    XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutes (
    UserID integer PRIMARY KEY,
    GuildID integer,
    EndTime text
);

CREATE TABLE IF NOT EXISTS warns (
    WarnID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID integer,
    GuildID integer,
    TimeOfViolation text,
    ActionBy integer,
    Reason text DEFAULT "No Reason Given",
    PolViolated text
);

CREATE TABLE IF NOT EXISTS starboard (
    RootMessageID integer PRIMARY KEY,
    StarMessageID integer,
    Stars integer DEFAULT 1
);