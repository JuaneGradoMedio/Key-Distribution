async def ready(client):
    print(client)

    for pending in client.pending_friends:
        await pending.decline()
    
    for friend in client.friends:
        await friend.remove()