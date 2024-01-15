import datetime
import logging
import goose
import fileManager
from discord.ext import commands

from config import ADMIN_IDS
from fileManager import load_command_tracker

from goose import GPT

COMMAND_MAX = 5  # Maximum number of executions
COOLDOWN_TIME = 86400  # Time in seconds (86400 secs in a day)


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_tracker = load_command_tracker()  # Dictionary that stores user_id: (count, last_reset_time)

    def get_command_tracker(self):
        return self.command_tracker

    # This command is limited to MAX numbers of executions per day per user
    @commands.command(name="heyGoose")
    async def ask_goose(self, ctx, *args):
        user_id = ctx.author.id
        username = ctx.author.name
        message = ''.join(args)

        # No command limit if admin
        if user_id in ADMIN_IDS:
            logging.info(f"Admin {username} has asked a question")
            response = await goose.call_goose(ctx, message)
            await ctx.send(response)
            return
        elif user_id in self.command_tracker:
            count, last_reset_time = self.command_tracker[user_id]
            seconds_elapsed = (datetime.datetime.now() - last_reset_time).total_seconds()

            if seconds_elapsed >= COOLDOWN_TIME:
                # After cooldown time reset count
                logging.info(f"{username} has asked 1 question")
                self.command_tracker[user_id] = (1, datetime.datetime.now())
                response = await goose.call_goose(ctx, message)
                await ctx.send(response)
            elif count < COMMAND_MAX:
                logging.info(f"{username} has asked {count + 1} questions")
                self.command_tracker[user_id] = (count + 1, last_reset_time)
                response = await goose.call_goose(ctx, message)
                await ctx.send(response)
            else:
                hh_mm_ss = str(datetime.timedelta(seconds=seconds_elapsed))
                await ctx.send(f"Dear seeker of knowledge, you have reached the boundary of questions that you may "
                               f"ask of me. Return in {hh_mm_ss} for more profound ponderings.")
        else:
            # First time user
            logging.info(f"{username} has asked 1 question")
            self.command_tracker[user_id] = (1, datetime.datetime.now())
            response = await goose.call_goose(ctx, message)
            await ctx.send(response)

    @commands.command(name="gooseProverb")
    async def get_proverb(self, ctx):
        can_execute = verify_prompt_limit(ctx)
        if can_execute:
            proverb = await goose.create_proverb(self.bot)
            await ctx.send(proverb)

    async def is_admin(self, ctx):
        user_id = ctx.author.id
        if user_id in ADMIN_IDS:
            return True
        else:
            await ctx.send(f"Apologies, dear {ctx.author.name}, but it appears the command you seek to wield is "
                           f"elusive to those entitled admin")
            return False
            
    async def verify_prompt_limit(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name

        # No command limit if admin
        if user_id in ADMIN_IDS:
            logging.info(f"Admin {username} has asked a question")
            return True
        elif user_id in self.command_tracker:
            count, last_reset_time = self.command_tracker[user_id]
            seconds_elapsed = (datetime.datetime.now() - last_reset_time).total_seconds()

            if seconds_elapsed >= COOLDOWN_TIME:
                # After cooldown time reset count
                logging.info(f"{username} has asked 1 question")
                self.command_tracker[user_id] = (1, datetime.datetime.now())
                return True
            elif count < COMMAND_MAX:
                logging.info(f"{username} has asked {count + 1} questions")
                self.command_tracker[user_id] = (count + 1, last_reset_time)
                return True
            else:
                hh_mm_ss = str(datetime.timedelta(seconds=seconds_elapsed))
                await ctx.send(f"Dear seeker of knowledge, you have reached the boundary of questions that you may "
                               f"ask of me. Return in {hh_mm_ss} for more profound ponderings.")
                return False
        else:
            # First time user
            logging.info(f"{username} has asked 1 question")
            self.command_tracker[user_id] = (1, datetime.datetime.now())
            return True


async def setup(bot):
    await bot.add_cog(CommandCog(bot))
