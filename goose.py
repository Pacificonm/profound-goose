import logging
import random
import config
import prompts
import requests
import GptUtilities
from fileManager import load_file
from openai import OpenAI
from config import GUILD_ID

# Constants
GPT_3_TURBO = "gpt-3.5-turbo"
GPT_4O = "gpt-4o"

PROVERB_THREAD = "proverb-thread"
CONVERSATION_THREAD = "convo-thread"
MAX_THREAD_SIZE = 10


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class GooseService:
    def __init__(self):
        self.GPT = OpenAI(api_key=config.GPT_KEY, default_headers={"OpenAI-Beta": "assistants=v2"})
        self.thread_log = load_file(config.THREAD_LOG_FILENAME)  # Tracks the size of a conversation thread

    def get_thread_log(self):
        return self.thread_log

    # Single prompt completion
    def create_single_completion(self, prompt):
        # Call the GPT API
        logging.debug("SENDING GPT REQUEST")
        return self.GPT.chat.completions.create(
            model=GPT_3_TURBO,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    async def create_daily_proverb(self, bot):
        proverb_type = random.randrange(4)  # Num between 0-3

        if proverb_type <= 2:
            # Write normal proverb
            return await self.get_goose_response(prompts.PROVERB, None, PROVERB_THREAD)
        else:
            # Write proverb for random user in guild
            guild = bot.get_guild(GUILD_ID)
            usernames = [member.name for member in guild.members if not member.bot]
            user = random.choice(usernames)
            return await self.get_goose_response(prompts.USER_PROVERB.format(username=user), None, PROVERB_THREAD)

    async def create_proverb(self):
        try:
            response = self.create_single_completion(prompts.PROVERB)
            return response.choices[0].message.content.strip('"')
        except Exception as e:
            return f'Error: {str(e)}'

    async def create_story(self, username):
        try:
            story_prompt = random.choice(prompts.STORIES)
            response = self.create_single_completion(story_prompt.format(username=username))
            return response.choices[0].message.content.strip('"')
        except Exception as e:
            return f'Error: {str(e)}'

    async def call_goose(self, ctx, user_message, username):
        user_message = user_message.replace('"', '\"')
        user_message = user_message.replace("\'", "")
        query = f"User \"{username}\" says:\n{user_message}"

        return await self.get_goose_response(query, None, CONVERSATION_THREAD)

    async def call_goose_attachment(self, ctx, user_message, username):
        query = f"User \"{username}\" says:\n{user_message}"
        try:
            attachment = ctx.message.attachments[0]
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif']):
                image_url = attachment.url
                response = requests.get(image_url)
                if response.status_code == 200:
                    return await self.get_goose_response(query, image_url, CONVERSATION_THREAD)
                else:
                    logging.warning(f'Error getting image URL: {str(response.status_code)}')
                    return (
                        "Ah, dear seeker of visual delights, alas, there was an error viewing your digital treasure. "
                        "Seek solace in the invisible wonders of the universe, for they hold truths that the eye "
                        "alone cannot perceive.")
            else:
                return (
                    "Ah, dear seeker of visual delights, the contents of your attachment eludes my grasp for I am not "
                    "familiar with its format. Embrace the intangible beauty of the unseen, for sometimes, "
                    "the unseen holds more wisdom than the visible.")
        except Exception as e:
            return f'Error: {str(e)}'

    async def get_goose_response(self, query, attachment_url, thread_log_key):
        if self.verify_thread_size(thread_log_key):
            # Add message to existing thread
            thread_id, thread_size = self.thread_log[thread_log_key]
            if attachment_url is None:
                response = await self.query_thread(thread_id, query)
            else:
                response = await self.query_thread_attachment(thread_id, query, attachment_url)
            self.thread_log[thread_log_key] = (thread_id, thread_size + 1)
            return response.strip('"')
        else:
            # Delete thread
            await self.delete_thread_log(thread_log_key)
            # Create new thread
            logging.debug("Creating new thread")
            thread_id = await GptUtilities.create_thread()
            if attachment_url is None:
                response = await self.query_thread(thread_id, query)
            else:
                response = await self.query_thread_attachment(thread_id, query, attachment_url)
            self.thread_log[thread_log_key] = (thread_id, 1)
            return response.strip('"')

    async def query_thread_attachment(self, thread_id, query, attachment_url):
        try:
            logging.debug("Adding message with attachment")
            await GptUtilities.add_attachment_message(thread_id, query, attachment_url)
            logging.debug("Running thread")
            return await GptUtilities.run_thread_get_response(thread_id, config.GOOSE_ASSISTANT_ID)
        except Exception as e:
            return f'Error: {str(e)}'

    async def query_thread(self, thread_id, query):
        try:
            logging.debug("Adding message")
            await GptUtilities.add_message(thread_id, query)
            logging.debug("Running thread")
            return await GptUtilities.run_thread_get_response(thread_id, config.GOOSE_ASSISTANT_ID)
        except Exception as e:
            return f'Error: {str(e)}'

    def verify_thread_size(self, thread_log_key):
        logging.debug("Verifying thread size")
        if thread_log_key in self.thread_log:
            thread_id, thread_size = self.thread_log[thread_log_key]
            if int(thread_size) < MAX_THREAD_SIZE:
                return True
            else:
                return False
        else:
            return False

    async def delete_thread_log(self, thread_log_key):
        logging.debug("Deleting thread")
        if thread_log_key in self.thread_log:
            thread_id, thread_size = self.thread_log[thread_log_key]
            await GptUtilities.delete_thread(thread_id)


# Singleton instance of the class
goose_service = GooseService()
