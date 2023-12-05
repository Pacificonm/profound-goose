import datetime
import logging
import goose

from discord.ext import commands

from goose import GPT

COMMAND_MAX = 5  # Maximum number of executions
COOLDOWN_TIME = 86400  # Time in seconds (86400 secs in a day)


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_tracker = {}  # Dictionary that stores user_id: (count, last_reset_time)

    # This command is limited to MAX numbers of executions per day per user
    @commands.command(name="heyGoose")
    async def ask_goose(self, ctx, *args):
        user_id = ctx.author.id
        message = ''.join(args)

        if user_id in self.command_tracker:
            count, last_reset_time = self.command_tracker[user_id]
            seconds_elapsed = (datetime.datetime.now() - last_reset_time).total_seconds()

            if seconds_elapsed >= COOLDOWN_TIME:
                # After cooldown time reset count
                logging.info(f"{user_id} has asked 1 question")
                self.command_tracker[user_id] = (1, datetime.datetime.now())
                await ctx.send(goose.call_goose(ctx, message))
            elif count < COMMAND_MAX:
                logging.info(f"{user_id} has asked {count + 1} questions")
                self.command_tracker[user_id] = (count + 1, last_reset_time)
                await ctx.send(goose.call_goose(ctx, message))
            else:
                hh_mm_ss = str(datetime.timedelta(seconds=seconds_elapsed))
                await ctx.send(f"Dear seeker of knowledge, you have reached the boundary of questions that you may "
                               f"ask of me. Return in {hh_mm_ss} for more profound ponderings.")
        else:
            # First time user
            logging.info(f"{user_id} has asked 1 question")
            self.command_tracker[user_id] = (1, datetime.datetime.now())
            await ctx.send(goose.call_goose(ctx, message))

#TODO: Implement proverb command and also proverbs about users
    # @commands.command(name="proverb")
    # async def get_proverb(self, ctx):
    #     proverb = goose.create_proverb()
    #     await ctx.send(proverb)


async def setup(bot):
    await bot.add_cog(CommandCog(bot))
