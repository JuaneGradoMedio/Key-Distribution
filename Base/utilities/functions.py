import discord, aiohttp, json, os, sys
from .constants import OWNERS, DEV

FORTNITE_API = "https://fortnite-api.com/v2/stats/br/v2"
FORTNITE_HEADERS = {
    "x-api-key": "fa4116d44822d15b9b762ca34704d608f7c0bab2"
}

def restart_program() -> None:
    """
    Restarts the bot
    """
    python = sys.executable
    os.execl(python, python, * sys.argv)

def getCredentials() -> dict:
    """
    Returns the credentials in the credentials file.
    
    :returns: dict
    """

    with open("./Base/configuration/credentials.json", "r") as f:
        return json.load(f)

def getConfig() -> dict:
    """
    Returns the content of the configuration file.
    
    :returns: dict
    """
    with open("./Base/configuration/config.json", "r") as f:
        return json.load(f)

def getBots(query:str = "online") -> list:
    """
    Returns the list of online bots.
    
    :param query: Union["online", "offline", "all"] 
    :returns: list
    """
    data = {}

    with open("./Base/configuration/fortnite_bots.json") as f:
        data = json.load(f)
    
    if query == "all":
        return data["online"] + data["offline"]
    elif query == "online":
        return data["online"]
    elif query == "offline":
        return data["offline"]
    
    raise "query parameter was not online, offline or all"

def na_getPrefix() -> str:
    """
    Gets the current prefix of the discord bot
    
    :returns: str
    """

    with open("./Base/configuration/config.json", "r") as f:
        return (json.load(f))["discord_prefix"]

async def getPrefix() -> str:
    """
    Gets the current prefix of the discord bot
    
    :returns: str
    """

    with open("./Base/configuration/config.json", "r") as f:
        return (json.load(f))["discord_prefix"]

async def check_owner(ctx) -> bool:
    """
    Checks if a user is an owner. Use with @commands.check()
    
    :param ctx: discord.ext.commands.Context
    :returns: bool
    """
    if ctx.author.id in OWNERS or ctx.author.id == DEV:
        return True

async def get_fortnite_account(IGN: str=None, accountType: str="epic", ID: str=None, image: bool=False) -> dict:
    """
    Search for an account's data on the Fortnite api and returns the results.
    
    :param IGN: str = None
    :accountType: str = "epic"
    :param ID: str = None
    :param image: bool = False
    :returns: dict
    """

    if ID:
        url = FORTNITE_API + f"/{ID}"
        if image:
            url += "?image=all"
    elif IGN:
        url = FORTNITE_API + f"?name={IGN}&accountType={accountType}"
        if image:
            url += "&image=all"

    async with aiohttp.ClientSession(headers=FORTNITE_HEADERS) as cs:
        async with cs.get(url) as r:
            res = await r.json()
            return res