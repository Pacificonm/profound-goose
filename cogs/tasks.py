import datetime

from discord.ext import commands, tasks
from goose import goose_service
from config import GOOSE_WISDOM


class TaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wisdom_message.start()

    @tasks.loop(time=datetime.time(hour=12, minute=0, second=0))  # 12:00 PM UTC == 7:00 AM EST
    async def wisdom_message(self):
        channel = self.bot.get_channel(GOOSE_WISDOM)

        proverb = await goose_service.create_daily_proverb(self.bot)

        await channel.send(proverb)

    @wisdom_message.before_loop
    async def before_wisdom_message(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(TaskCog(bot))
