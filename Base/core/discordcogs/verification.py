import sys
sys.path.append(".")

import discord, asyncio, random
from discord.ext import commands
from discord.utils import get
from discord_slash.utils.manage_components import ComponentContext, create_actionrow, create_button, wait_for_component
from datetime import datetime
from Base.utilities import *
from Base.utilities.constants import FSC_IMAGE, COLOURS

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        if ctx.component["custom_id"] == "verification":
            data = await self.bot.db.find_one({"guild_id": ctx.guild.id})
            await ctx.defer(hidden=True)

            verified_users = self.bot.verified_db
            search = await verified_users.find_one({"discord_id": ctx.author_id})

            if search: # Verified in another server
                d = await get_fortnite_account(ID=search["epic_id"])
                ign = d["data"]["account"]["name"]
                if ctx.guild_id in search["servers_verified"]:
                    embed = discord.Embed(
                        title="Verificado",
                        description=f"Ya estás verificado en este servidor\n\n> **Nombre de epic**: {ign}",
                        color=COLOURS["green"],
                        timestamp=datetime.now()
                    )

                    b0 = create_button(style=4, label="Desvincularse", custom_id="0")

                    components = [create_actionrow(b0)]
                    sent = await ctx.author.send(embed=embed, components=components)
                    await ctx.send(f"Te he envíado un [mensaje directo]({sent.jump_url})", hidden=True)

                    try:
                        interaction = await wait_for_component(self.bot, messages=sent, timeout=30)
                    except asyncio.TimeoutError:
                        await sent.edit(content=f"Se ha caducado este mensaje, vuelve a <#{ctx.channel_id}> y dale otra vez al botón para verificarte!", components=[])
                    
                    if interaction:
                        await interaction.defer(edit_origin=True)
                        
                        selected = interaction.component

                        verified_users = []
                        servers_verified = []
                        if "verified_users" in data and data["verified_users"] != None:
                            verified_users = data["verified_users"]
                        
                        if "servers_verified" in search or search["servers_verified"] != None:
                            servers_verified = search["servers_verified"]

                        if ctx.author.id in verified_users: verified_users.pop(verified_users.index(ctx.author.id))
                        if ctx.guild.id in servers_verified: servers_verified.pop(servers_verified.index(ctx.guild_id))

                        await self.bot.db.update_one({"guild_id": str(ctx.guild.id)}, {"verified_users": verified_users})
                        await self.bot.verified_db.update_one({"discord_id": ctx.author.id}, {"servers_verified": servers_verified})

                        member = ctx.author
                        if not isinstance(ctx.author, discord.Member):
                            member = get(ctx.guild.members, id=ctx.author.id)
                            if not member:
                                member = await ctx.guild.fetch_message(ctx.author.id)

                        if "config" in data and "vfrole" in data["config"] and data["config"]["vfrole"] != "":
                            role = get(ctx.guild.roles, id=data["config"]["vfrole"])
                            if role in member.roles:
                                await member.remove_roles(role)
                        
                        if "config" in data and "vfnick" in data["config"] and data["config"]["vfnick"] == True:
                            if member.nick == ign:
                                await member.edit(nick=None)
                        
                        embed = discord.Embed(
                            title="Desvinculado",
                            description="Te has desvinculado en el servidor",
                            color=COLOURS["green"]
                        )

                        await interaction.edit_origin(embed=embed, components=[])
                    
                    return
                      
                else:
                    d = await get_fortnite_account(ID=search["epic_id"])
                    ign = d["data"]["account"]["name"]
                    embed = discord.Embed(
                        title="Verificación",
                        description=f"Veo que ya te has verificado en otro servidor, quieres volver a usar esta cuenta?\n\n> **Nombre de epic**: {ign}",
                        color=COLOURS["blue"],
                        timestamp=datetime.now()
                    )
                    embed.set_footer(text="Verificación FSC")
                    embed.set_thumbnail(url=FSC_IMAGE)

                    b1 = create_button(style=1, label=f"Usar {ign}", custom_id="0")
                    b2 = create_button(style=3, label="Víncular otra cuenta", custom_id="1")
                    components = [create_actionrow(b1, b2)]

                    sent = await ctx.author.send(embed=embed, components=components)
                    await ctx.send(f"Te he envíado un [mensaje directo]({sent.jump_url})", hidden=True)

                    try:
                        interaction = await wait_for_component(self.bot, messages=sent, timeout=30)
                    except asyncio.TimeoutError:
                        await sent.edit(content=f"Se ha caducado este mensaje, vuelve a <#{ctx.channel_id}> y dale otra vez al botón para verificarte!", components=[])
                        return
                    
                    if interaction:
                        await interaction.defer(edit_origin=True)

                        selected = interaction.component

                        if selected["custom_id"] == "0":
                            embed = discord.Embed(
                                title = "Verificado",
                                desciption="Te has verificado correctamente!",
                                color=COLOURS["green"],
                                timestamp=datetime.now()
                            )

                            member = ctx.author
                            if not isinstance(ctx.author, discord.Member):
                                member = get(ctx.guild.members, id=ctx.author.id)
                                if not member:
                                    member = await ctx.guild.fetch_message(ctx.author.id)
                            
                            if "config" in data and data["config"] and "vfrole" in data["config"] and data["config"] and data["config"]["vfrole"] != "":
                                    role = get(ctx.guild.roles, id=data["config"]["vfrole"])
                                    if not role in member.roles:
                                        try:
                                            await member.add_roles(role)
                                        except:
                                            pass
                            
                            if "config" in data and  "vfnick" in data["config"] and data["config"]["vfnick"] == True:
                                try:
                                    await member.edit(nick=ign)
                                except:
                                    pass

                            if "verified_users" in data and data["verified_users"] is not None:
                                    data["verified_users"].append(ctx.author.id)
                            else:
                                data["verified_users"] = [ctx.author.id]

                            await self.bot.db.update_one({"guild_id": str(ctx.guild.id)}, data)
                            await self.bot.verified_db.update_one({"discord_id": ctx.guild_id}, search)

                            await interaction.edit_origin(embed=embed, components=[])
                            return
                        
                        else:
                            pass
                            
            else: # Not verified anywhere
                pass
            bots = getBots("online")
            add = random.choice(bots)

            embed = discord.Embed(
                title="Verificación",
                description=f"Para verificarte, debes agregar a:\n```\n{add}```\nUna vez añadido tendras que enviar el codigo que te aparece en el Bot!",
                color=COLOURS["blue"],
                timestamp=datetime.now()
            )
            sent = await ctx.author.send(embed=embed)
            await ctx.send(f"Te he envíado un [mensaje directo]({sent.jump_url})", hidden=True)

            run = True
            while run:
                try:
                    res = await self.bot.wait_for("message", check=lambda m: isinstance(m.channel, discord.DMChannel) and m.channel.recipient.id == m.author.id == ctx.author.id, timeout=120)
                except asyncio.TimeoutError:
                    embed = discord.Embed(
                        title="Verificación expirada",
                        description="Se ha expirado el tiempo para completar la verificación.",
                        color=COLOURS["red"]
                    )
                    embed.set_footer(text="Verificación FSC")
                    await sent.edit(embed=embed)

                    run = False
                    return
            
                if res:
                    find = await self.bot.verifying_db.find_all()
                    if find: codes = [str(d["code"]) for d in find]
                    else: codes = []
                    try:
                        codeint = int(res.content)
                        code = res.content
                    except:
                        await res.reply("Esto no es un número válido.")
                        code = None
                    if code:
                        if str(code) in codes:
                            search = await self.bot.verifying_db.find_one({"code": int(code)})

                            if search:
                                epic_id = search["epic_id"]
                                d = await get_fortnite_account(ID=epic_id)
                                epic_ign = d["data"]["account"]["name"]

                                await self.bot.verifying_db.delete_one({"code": int(code)})

                                member = ctx.author
                                if not isinstance(ctx.author, discord.Member):
                                    member = get(ctx.guild.members, id=ctx.author.id)
                                    if not member:
                                        member = await ctx.guild.fetch_message(ctx.author.id)

                                if "config" in data and data["config"] and "vfrole" in data["config"] and data["config"] and data["config"]["vfrole"] != "":
                                    role = get(ctx.guild.roles, id=data["config"]["vfrole"])
                                    if not role in member.roles:
                                        try:
                                            await member.add_roles(role)
                                        except:
                                            pass
                                
                                if "config" in data and data["config"] and "vfnick" in data["config"] and data["config"] and data["config"]["vfnick"] == True:
                                    try:
                                        await member.edit(nick=epic_ign)
                                    except:
                                        pass

                                if "verified_users" in data and data["verified_users"] is not None:
                                    data["verified_users"].append(ctx.author.id)
                                else:
                                    data["verified_users"] = [ctx.author.id]
                                ins = {"discord_id": ctx.author.id, "epic_id": epic_id, "servers_verified": [ctx.guild_id], "data": d}

                                await self.bot.db.update_one({"guild_id": str(ctx.guild.id)}, data)

                                s = await self.bot.verified_db.find_one({"discord_id": str(ctx.author.id)})
                                if s:
                                    await self.bot.verified_db.update_one({"discord_id": ctx.author.id}, {"servers_verified": [ctx.guild.id]})
                                else:
                                    await self.bot.verified_db.insert(ins)

                                embed = discord.Embed(
                                    title="Verificado",
                                    description=f"Te has verificado correctamente con la cuenta {epic_ign}",
                                    color=COLOURS["green"]
                                )

                                await ctx.author.send(embed=embed)
                                run = False
                                return
                            
                    await ctx.author.send(f"El código `{code}` no es válido")

def setup(bot):
    bot.add_cog(Verification(bot))