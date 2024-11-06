from datetime import datetime, timezone, timedelta
import logging
from discord.ext import commands

import config
from fileManager import load_file
from goose import goose_service

COMMAND_MAX = 5  # Maximum number of executions
COOLDOWN_TIME = 86400  # Time in seconds (86400 secs in a day)


def calculate_time(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format the result as hh:mm:ss
    return f'{hours:02}:{minutes:02}:{seconds:02}'


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_tracker = load_file(
            config.COMMAND_TRACKER_FILENAME)  # Dictionary that stores user_id: (count, last_reset_time)

    def get_command_tracker(self):
        return self.command_tracker

    @commands.command(name="heyGoose", help="Say anything you like to the Goose and he will respond. Image "
                                            "attachments are supported.")
    async def ask_goose(self, ctx, *args):
        message = ' '.join(args)
        is_allowed = await self.verify_prompt_limit(ctx)
        if is_allowed:
            username = ctx.author.name
            if ctx.message.attachments:
                logging.info("Goose question contains attachment")
                response = await goose_service.call_goose_attachment(ctx, message, username)
                await ctx.send(response)
            else:
                response = await goose_service.call_goose(ctx, message, username)
                await ctx.send(response)

    @commands.command(name="gooseStory", help="The Goose tells a story about himself. Memory not supported.")
    async def goose_story(self, ctx):
        is_allowed = await self.verify_prompt_limit(ctx)
        if is_allowed:
            username = ctx.author.name
            response = await goose_service.create_story(username)
            await ctx.send(response)

    @commands.command(name="gooseProverb", help="The Goose responds with a proverb. Memory not supported.")
    async def goose_proverb(self, ctx):
        is_allowed = await self.verify_prompt_limit(ctx)
        if is_allowed:
            proverb = await goose_service.create_proverb()
            await ctx.send(proverb)

    @commands.command(name="help", help="Displays all commands with descriptions.")
    async def custom_help(self, ctx):
        command_list = sorted([
            f".{command.name} - {command.help}" for command in self.bot.commands
        ])
        # Join each formatted command into a single string
        commands_string = "\n\n".join(command_list)
        # Send the formatted list to the user
        await ctx.send(f"Command list:\n```{commands_string}```")

    async def is_admin(self, ctx):
        user_id = ctx.author.id
        if user_id in config.ADMIN_IDS:
            return True
        else:
            await ctx.send(f"Apologies, dear {ctx.author.name}, but it appears the command you seek to wield is "
                           f"elusive to those entitled admin")
            return False

    async def verify_prompt_limit(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name

        # No command limit if admin
        if user_id in config.ADMIN_IDS:
            logging.info(f"Admin {username} has asked a question")
            return True
        elif user_id in self.command_tracker:
            count, last_reset_time = self.command_tracker[user_id]
            seconds_elapsed = (datetime.now(timezone.utc) - last_reset_time).total_seconds()

            if seconds_elapsed >= COOLDOWN_TIME:
                # After cooldown time reset count
                logging.info(f"{username} has asked 1 question")
                self.command_tracker[user_id] = (1, datetime.now(timezone.utc))
                return True
            elif count < COMMAND_MAX:
                logging.info(f"{username} has asked {count + 1} questions")
                self.command_tracker[user_id] = (count + 1, last_reset_time)
                return True
            else:
                time_remaining = calculate_time(COOLDOWN_TIME - int(seconds_elapsed))
                await ctx.send(f"Dear seeker of knowledge, you have reached the boundary of questions that you may "
                               f"ask of me. Return in {time_remaining} for more profound ponderings.")
                return False
        else:
            # First time user
            logging.info(f"{username} has asked 1 question")
            self.command_tracker[user_id] = (1, datetime.now(timezone.utc))
            return True


async def setup(bot):
    await bot.add_cog(CommandCog(bot))
