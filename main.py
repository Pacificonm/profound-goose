import os
import logging
import config
import discord
from discord.ext import commands

from fileManager import save_command_tracker

# Profound Goose
# Version 1.2.1

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

# set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)


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


# TODO: Get file writer working on bot exit. Currently does not save tracker dic on app close

# @bot.event
# async def on_disconnect():
#     cog = bot.get_cog("cogs.commands")
#     if cog:
#         tracker = cog.get_command_tracker()
#         save_command_tracker(tracker)
#     logging.critical("Bot disconnected")



# Start bot
try:
    bot.run(config.DISCORD_TOKEN)
except KeyboardInterrupt:
    logging.error("INTERRUPT")
    command_cog = bot.get_cog("cogs.commands")
    if command_cog:
        command_tracker = command_cog.get_command_tracker()
        save_command_tracker(command_tracker)
    bot.close()
