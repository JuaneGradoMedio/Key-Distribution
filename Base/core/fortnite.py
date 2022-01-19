import sys
sys.path.append(".")

import fortnitepy, json, crayons, functools, threading, asyncio
from Base.core.fortnitecogs import *
from Base.core.discord import DiscordBot
from Base.utilities.functions import getConfig, getCredentials

class AllFortniteBots():
    def __init__(self, credentials: dict, discord: bool = False):
        """
        Init all Fortnite bots, need to pass credentials and if you want to init the Discord bot too!
        
        :param credentials: dict
        :param discord: bool = False
        :returns: AllFortniteBots
        """

        self.clients = []
        self._discord = discord
        self._credentials = credentials
    
    def run(self):
        for e, p in self._credentials.items():
            device_auths = self.get_device_details().get(e, {})
            authentication = fortnitepy.AdvancedAuth(
                email=e,
                password=p,
                prompt_authorization_code=True,
                prompt_code_if_invalid=True,
                delete_existing_device_auths=True,
                **device_auths
            )

            client = fortnitepy.Client(
                auth=authentication,
                default_party_member_config=fortnitepy.DefaultPartyMemberConfig(
                    meta=(
                        functools.partial(fortnitepy.ClientPartyMember.set_outfit, 'CID_175_Athena_Commando_M_Celestial'), # galaxy skin
                    )
                )
            )

            # register events here
            client.add_event_handler("device_auth_generate", self.event_device_auth_generate)
            client.add_event_handler("event_friend_request", verification)
            client.add_event_handler("event_sub_ready", ready)

            # client.add_event_handler('device_auth_generate', event_device_auth_generate)
            # client.add_event_handler('friend_request', event_sub_friend_request)
            # client.add_event_handler('party_member_join', event_sub_party_member_join)

            self.clients.append(client)

        if self._discord:
            discordBot = DiscordBot()
            loop1 = asyncio.get_event_loop()
            loop1.create_task(discordBot.run(getConfig()["discord_token"]))
            threading.Thread(target=loop1.run_forever).start()
        
        #thread2 = threading.Thread(target=fortnitepy.run_multiple, args=(self.clients, ))
        fortnitepy.run_multiple(
            self.clients,
            ready_callback=self.event_sub_ready,
            all_ready_callback=self.all_ready,
            before_close=self.before_close
        )

    def get_device_details(self) -> dict:
        """
        Gets the device details.
        
        :returns: dict
        """

        with open("./Base/configuration/device_auths.json", "r") as f:
            return json.load(f)
        
        return {}
    
    def store_device_details(self, email: str, details: dict) -> None:
        """
        Stores new device details.

        :param email: str
        :param details: dict
        :returns: None
        """

        current = self.get_device_details()
        current[email] = details

        with open("./Base/configuration/device_auths.json", "w") as w:
            json.dump(current, w, indent=4)
        
    async def event_device_auth_generate(self, details: str, email: dict) -> None:
        """
        When a new auth is generate, save the details.

        :param email: str
        :param details: dict
        :returns: None
        """

        self.store_device_details(email, details)
    
    async def event_sub_ready(self, client):
        with open("./Base/configuration/fortnite_bots.json", "r") as f:
            f = json.load(f)
            if client.user.display_name in f["offline"]:
                f["offline"].pop(f["offline"].index(client.user.display_name))
            
            f["online"].append(client.user.display_name)
        
            with open("./Base/configuration/fortnite_bots.json", "w") as w:
                json.dump(f, w, indent=4)

        print(crayons.green(f"[FORTNITE] Bot online, username: {client.user.display_name}"))
        
    
    async def before_close(self):
        with open("./Base/configuration/fortnite_bots.json", "r") as f:
            f = json.load(f)
            f["offline"] = f["online"] + f["offline"]
            f["online"] = []
        
            with open("./Base/configuration/fortnite_bots.json", "w") as w:
                json.dump(f, w, indent=4)

    async def all_ready(self):
        print(crayons.green("[FORTNITE] All bots online"))

        # if self._discord:
        #     discord = DiscordBot()
        #     discord.run(getConfig()["discord_token"])