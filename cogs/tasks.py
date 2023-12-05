import datetime
import logging

from discord.ext import commands, tasks
import goose

GOOSE_WISDOM = 1181051538278469783


class TaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wisdom_message.start()

    @tasks.loop(time=datetime.time(hour=8, minute=0, second=0))  # 8:00 AM UTC == 3:00 AM EST
    async def wisdom_message(self):
        channel = self.bot.get_channel(GOOSE_WISDOM)

        proverb = goose.create_proverb()

        await channel.send(proverb)


async def setup(bot):
    await bot.add_cog(TaskCog(bot))
