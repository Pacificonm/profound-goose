from discord.ext import commands


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Return if bot message
        if message.author == self.bot.user:
            return

        # Return if command message
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        keywords = ['badword']

        # Check if the message contains any of the keywords
        if any(keyword in message.content.lower() for keyword in keywords):
            await message.delete()  # Delete the message
            await message.channel.send(f"A message containing a restricted word was deleted.")

        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(EventCog(bot))
