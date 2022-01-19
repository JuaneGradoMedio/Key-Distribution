import discord, crayons
from discord.ext import commands

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, extension_name):  
        await ctx.message.delete()
        self.bot.load_extension(f"core.discordcogs.{extension_name}")
        await ctx.send(f"{ctx.author.mention}, loaded `{extension_name}`.", delete_after=3)
        print(crayons.cyan(f"[DISCORD] {ctx.author.name} loaded {extension_name}"))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, extension_name):
        await ctx.message.delete()
        self.bot.unload_extension("core.discordcogs."+extension_name)
        await ctx.send(f"{ctx.author.mention}, unloaded `{extension_name}`.", delete_after=3)
        print(crayons.cyan(f"[DISCORD] {ctx.author.name} unloaded {extension_name}"))

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, extension_name):
        await ctx.message.delete()
        self.bot.reload_extension("core.discordcogs."+extension_name)
        await ctx.send(f"{ctx.author.mention}, reloaded `{extension_name}`.", delete_after=3)
        print(crayons.cyan(f"[DISCORD] {ctx.author.name} reloaded {extension_name}"))

def setup(bot):
    bot.add_cog(Developer(bot))