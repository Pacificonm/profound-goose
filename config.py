import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_KEY')
GPT_KEY = os.getenv('GPT_API_KEY')