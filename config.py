import os
from dotenv import load_dotenv

# TODO: Turn this into a config class

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_KEY_TEST')
GPT_KEY = os.getenv('GPT_API_KEY')

GUILD_ID = 1179592066846699561 #int(os.getenv('GUILD_ID'))

# Wisdom text channel
GOOSE_WISDOM = int(os.getenv('GOOSE_WISDOM'))

ADMIN_IDS = [292848029269098507, 217274120625324032]
