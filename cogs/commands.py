import discord
from discord.ext import commands


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def speak(self, ctx):
        print("speak triggered")
        await ctx.channel.send('Hello world!')


async def setup(bot):
    await bot.add_cog(CommandCog(bot))
