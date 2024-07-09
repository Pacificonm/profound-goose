import os
import logging
import config
import discord
from discord.ext import commands

from goose import goose_service
from fileManager import save_file


# Profound Goose
# Version 2.0.0

class MyBot(commands.Bot):

    # Override close method to shut down gracefully
    async def close(self):
        logging.info("Gracefully shutting down")
        command_cog = self.get_cog("CommandCog")

        # Save command tracker
        logging.debug("Saving command tracker")
        if command_cog:
            command_tracker = command_cog.get_command_tracker()
            save_file(command_tracker, config.COMMAND_TRACKER_FILENAME)

        # Save threads
        logging.debug("Saving thread log")
        thread_log = goose_service.get_thread_log()
        save_file(thread_log, config.THREAD_LOG_FILENAME)

        await super().close()


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

# set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = MyBot(command_prefix='.', intents=intents)


# load cogs
@bot.event
async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog = filename[:-3]
            logging.info(f"Loading cog {cog}")
            await bot.load_extension(f"cogs.{cog}")

    logging.info("Setup complete")


@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')


# Start bot
bot.run(config.DISCORD_TOKEN)
