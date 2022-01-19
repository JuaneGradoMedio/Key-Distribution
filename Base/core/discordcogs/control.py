import discord
from discord.ext import commands
from discord.utils import get
import json
import asyncio
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from Base.utilities import restart_program, getConfig

class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=["apagar"])
    @commands.is_owner()
    async def off(self, ctx):
        if ctx.author.id == 427146305651998721:
            bt = create_button(label="Confirm", style=3)#, emoji="✅")
            components = [create_actionrow(bt)]

            message = await ctx.message.reply(f"{ctx.author.mention} are you sure you want to do this?", components=components)

            try:
                confirmation = await wait_for_component(self.bot, messages=message, check= lambda i: i.author.id == ctx.author.id, timeout=10)
            except asyncio.TimeoutError:
                bt["disabled"] = True
                await message.edit(content="Expired", components=components)
                return
            if confirmation:
                await ctx.send("Turning off...")
                await message.delete()
                await ctx.message.delete()
                await self.bot.close()
                
    
    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        if ctx.author.id == 427146305651998721:
            read = getConfig()

            bt = create_button(label="Confirm", style=3)#, emoji="✅")
            components = [create_actionrow(bt)]

            message = await ctx.send(f"{ctx.author.mention} are you sure you want to do this?", components=components)
            try:
                confirmation = await wait_for_component(self.bot, messages=message, check= lambda i: i.author.id == ctx.author.id, timeout=10)
            except asyncio.TimeoutError:
                bt["disabled"] = True
                await message.edit(content="Expired", components=components)
                return
            if confirmation:
                bt["disabled"] = True
                await confirmation.edit_origin(content="Restarting... <a:loading:799293089633533953>", components=components)
                with open("./configuration/config.json", "w") as f:
                    read["restart_channel"] = ctx.channel.id
                    read["restart_message"] = message.id
                    json.dump(read, f, indent=2)

                await ctx.message.delete()
                restart_program()
            

def setup(bot):
    bot.add_cog(Control(bot))