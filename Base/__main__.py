from core.discord import DiscordBot
from core.fortnite import AllFortniteBots
from utilities import getCredentials, getConfig
import threading, asyncio

if __name__ == "__main__":
    discordBot = DiscordBot()
    fortniteBot = AllFortniteBots(credentials=getCredentials())

    loop = asyncio.get_event_loop()
    loop.create_task(discordBot.start(getConfig()["discord_token"]))
    loop.create_task(fortniteBot.run())
    threading.Thread(target=loop).start()