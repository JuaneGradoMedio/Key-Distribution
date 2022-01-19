import sys

from discord.ext.commands.core import check

sys.path.append(".")

import discord, time, asyncio
from discord.ext import commands
from discord.utils import get
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from datetime import datetime
from Base.utilities import *
from Base.utilities.constants import FSC_IMAGE

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    @commands.check(check_owner)
    async def config(self, ctx):
        if not ctx.invoked_subcommand:
            f_guild = await self.bot.db.find_one({"guild_id": ctx.guild.id})

            if not f_guild:
                f_guild = {"guild_id": ctx.guild.id, "config": {}, "verified_users": []}

                await self.bot.db.insert(f_guild)
            
            config = f_guild["config"]
            text = f"> **Prefijo(s)** - {(await getPrefix())}\n"

            text += "> **Canal de verificación** - "
            if "vfchannel" in config and config["vfchannel"]:
                text += f"<#{config['vfchannel']}>"
            text += "\n"

            text += "> **Role de verificado** - "
            if "vfrole" in config and config["vfrole"]:
                text += f"<@&{config['vfrole']}>"
            text += "\n"

            text += "> **Cambio el apodo de verificados** - "
            if "vfnick" in config and config["vfnick"] is not None:
                text += "Sí" if config["vfnick"] == True else "No"
            text += "\n"

            embed = discord.Embed(
                title="Configuración del servidor",
                description=text,
                color=ctx.guild.me.top_role.color.value,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=FSC_IMAGE)
            embed.set_footer(text="Verificación FSC")

            await ctx.reply(embed=embed)
    
    @config.command(aliases=["commands"])
    @commands.check(check_owner)
    async def channel(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            await ctx.reply("No has seleccionado el canal que quieres usar de verificación")
            return

        b = create_button(style=3, label="Verifícate", emoji=discord.PartialEmoji(name="Yes", id=855446951092682762, animated=False), custom_id="verification")
        components = [create_actionrow(b)]

        embed = discord.Embed(
            title="Verificación FSC",
            description="Reaccione con un emoticono para verificar su cuenta de Epic Games, a continuación recibirá un Mensaje directo, en el cual debe seguir los pasos indicados.",
            color=0x00ff00
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/754806741069201429/789257441170030612/PNG_2.png")
        embed.set_footer(text="Developed by FSC")

        sent = await channel.send(embed=embed, components=components)

        guild = await self.bot.db.find_one({"guild_id": ctx.guild.id})
        create = False
        if not guild:
            guild = {"guild_id": ctx.guild.id, "config": {}}
            create = True

        guild["config"]["vfchannel"] = channel.id

        if create:
            await self.bot.db.insert(guild)
        else:
            await self.bot.db.update_one({"guild_id": str(ctx.guild.id)}, {"config": guild["config"]})
        
        await ctx.reply(f"He envíado el mensaje a {channel.mention}")
    
    @config.command(aliases=["rol"])
    @commands.check(check_owner)
    async def role(self, ctx, role:discord.Role=None):
        if not role:
            await ctx.reply("No has seleccionado el rol que quieres que dé cuando la gente se verifique")
            return
        
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.reply(f"El rol {role.mention} está por encima de mi en la lista de roles y no puedo dar ese rol :(", allowed_mentions=discord.AllowedMentions(roles=False))
            return
        
        f_guild = await self.bot.db.find_one({"guild_id": ctx.guild.id})
        if not f_guild:
            f_guild = {"guild_id": ctx.guild.id, "config": {}, "verified_users": []}
            await self.bot.db.insert(f_guild)
        
        config = f_guild["config"]
        old = None

        if "vfrole" in config:
            old = config["vfrole"]
        
        config["vfrole"] = role.id

        if not old:
            text = f"Has seleccionado el rol {role.mention} como rol de verificados"
        else:
            text = f"Has cambiado el rol de verificados de <@&{old}> a {role.mention}"
        
        await self.bot.db.update_one({"guild_id": str(ctx.guild.id)}, {"config": config})
        
        await ctx.reply(text, allowed_mentions=discord.AllowedMentions(roles=False))

    @config.command(aliases=["nickname", "apodo"])
    @commands.check(check_owner)
    async def nick(self, ctx):
        f_guild = await self.bot.db.find_one({"guild_id": ctx.guild.id})
        if not f_guild:
            f_guild = {"guild_id": ctx.guild.id, "config": {}, "verified_users": []}
            await self.bot.db.insert(f_guild)
        
        config = f_guild["config"]
        current = "deshabilitado"

        b0 = create_button(style=3, label="Habilitar", custom_id="0")
        b1 = create_button(style=4, label="Deshabilitar", custom_id="1")
        components = [create_actionrow(b0, b1)]

        if "vfnick" in config:
            if config["vfnick"] == True:
                current = "habilitado"
            
        m = await ctx.reply(f"Selecciona si quieres habilitar o deshabilitar que cambie el apodo al verificarse.\n\n> Actualmente está **{current}**", components=components)

        try:
            interaction = await wait_for_component(self.bot, messages=m)
        except asyncio.TimeoutError:
            await m.edit(f"Actualmente está **{current}**", components=[])
            return
        
        if interaction:
            await interaction.defer(edit_origin=True)
            selected = interaction.component["custom_id"]

            if selected == "0":
                new = "habilitado"
            else:
                new = "deshabilitado"
            
            if new == current:
                await interaction.edit_origin("No has cambiado nada", components=[])
            
            else:
                if new == "habilitado":
                    config["vfnick"] = True
                else:
                    config["vfnick"] = False
                
                await self.bot.db.update_one({"guild_id": str(ctx.guild.id)}, {"config": config})
                await interaction.edit_origin(content=f"Has {new} correctamente que cambie los apodos de la gente verificada!", components=[])

    @commands.command()
    async def ping(self, ctx):
        t1 = time.time()
        msg = await ctx.reply("Pinging...")
        t2 = time.time()

        api_latency = round((t2 - t1 ) * 1000)
        heartbeat = round(self.bot.latency * 1000)

        await msg.edit(content=f"Pong! 🏓 \n\n> Heartbeat: `{heartbeat}ms`\n> API Latency: `{api_latency}ms`")

def setup(bot):
    bot.add_cog(Commands(bot))