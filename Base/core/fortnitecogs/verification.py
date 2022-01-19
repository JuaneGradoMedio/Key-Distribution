import sys
sys.path.append(".")

import random, asyncio
from fortnitepy.ext import commands
from Base.utilities import *

async def verification(request):
    """
    Verification from Fortnite POV. - Called when a friend request is detected.

    :param request: fortnitepy.BaseRequest
    :returns: None
    """
    if request.inbound:
        verifying = DataBase(path="verifying.db", keys=["discord_id", "epic_id", "code"])

        c = random.randint(1, 999999)

        search = await verifying.find_one({"epic_id": request.id})
        if search:
            c = search["code"]
        else:
            ins = {"epic_id": request.id, "code": c}
            await verifying.insert(ins)

        await request.accept()
        await request.client.send_presence(status=str(c), to=request.jid)

        await asyncio.sleep(300)
        await verifying.delete_one({"code": c})
        await request.decline()
