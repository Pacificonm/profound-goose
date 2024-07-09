import os
import json
from dotenv import load_dotenv

# TODO: Turn this into a config class

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_KEY_TEST')
GPT_KEY = os.getenv('GPT_API_KEY')
GOOSE_ASSISTANT_ID = os.getenv('GOOSE_ASSISTANT_ID')

GUILD_ID = int(os.getenv('GUILD_ID'))

# Wisdom text channel
GOOSE_WISDOM = int(os.getenv('GOOSE_WISDOM'))

ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS'))

COMMAND_TRACKER_FILENAME = "command_tracker.json"
THREAD_LOG_FILENAME = "thread_log.json"
