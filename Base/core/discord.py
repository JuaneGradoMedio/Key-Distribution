import sys
sys.path.append(".")

import discord, json, crayons, time
from discord_slash import SlashCommand
from discord.ext import commands
from discord.utils import get
from Base.utilities import *

class DiscordBot(commands.AutoShardedBot):
    def __init__(self):        
        allowed_mentions = discord.AllowedMentions(
            roles=False, everyone=False, users=True, replied_user=True
        )
        super().__init__(
            allowed_mentions=allowed_mentions,
            command_prefix=commands.when_mentioned_or(na_getPrefix()),
            case_insensitive=True,
            intents=discord.Intents.all(),
        )
        SlashCommand(self)

        self.loaded = []
        self.db = DataBase(path="guilds.db", keys=["guild_id", "config", "verified_users"])
        self.verified_db = DataBase(path="verified.db", keys=["discord_id", "epic_id", "servers_verified", "data"])
        self.verifying_db = DataBase(path="verifying.db", keys=["discord_id", "epic_id", "code", "bot_id"])

    
    async def on_ready(self):
        print(crayons.cyan(f"[DISCORD] Starting - User: {str(self.user)}"))
        await self.change_presence(
            status = discord.Status.online, 
            activity = None
        )

        startup_extensions = getConfig()["discord_startup_extensions"]
        for extension in startup_extensions:
            self.load_extension("core.discordcogs." + extension)

        print(crayons.cyan("[DISCORD] Bot started"))