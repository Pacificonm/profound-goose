import os
import logging
import config
import discord
from discord.ext import commands

# Profound Goose
# Version 1.1.0

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

# set up intents
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='.', intents=intents)


# load cogs
@client.event
async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog = filename[:-3]
            logging.info(f"Loading cog {cog}")
            await client.load_extension(f"cogs.{cog}")

    logging.info("Setup complete")


@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')


# Start bot
client.run(config.DISCORD_TOKEN)
