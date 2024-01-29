import logging
import random
import config
import prompts
import requests
from openai import OpenAI
from config import GUILD_ID

GPT = OpenAI(api_key=config.GPT_KEY)


# Single prompt completion
def create_single_completion(prompt):
    # Call the GPT API
    logging.debug("SENDING GPT REQUEST")
    return GPT.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


# Double prompt completion
def create_double_completion(instruction_prompt, user_prompt):
    # Call the GPT API
    logging.debug("SENDING GPT REQUEST")
    return GPT.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": instruction_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )


# Attachment prompt completion
def create_attachment_completion(instruction_prompt, user_prompt, attachment_url):
    # Call the GPT API
    logging.debug("SENDING GPT REQUEST")
    return GPT.chat.completions.create(
        model="gpt-4-vision-preview",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": instruction_prompt
            },
            {
                "role": "user",
                "content": [
                    user_prompt,
                    {
                        "type": "image_url",
                        "image_url": {"url": attachment_url},
                    }
                ]
            }
        ]
    )


async def create_daily_proverb(bot):
    proverb_type = random.randrange(4)  # Num between 0-3
    try:
        if proverb_type <= 2:
            # Write normal proverb
            response = create_single_completion(prompts.PROVERB)
        else:
            # Write proverb for random user in guild
            guild = bot.get_guild(GUILD_ID)
            usernames = [member.name for member in guild.members if not member.bot]
            user = random.choice(usernames)
            response = create_single_completion(prompts.USER_PROVERB.format(username=user))

        return response.choices[0].message.content.strip('"')
    except Exception as e:
        return f'Error: {str(e)}'


async def create_proverb():
    try:
        response = create_single_completion(prompts.PROVERB)
        return response.choices[0].message.content.strip('"')
    except Exception as e:
        return f'Error: {str(e)}'


async def create_story(username):
    try:
        story_prompt = random.choice(prompts.STORIES)
        response = create_single_completion(story_prompt.format(username=username))
        return response.choices[0].message.content.strip('"')
    except Exception as e:
        return f'Error: {str(e)}'


async def call_goose(ctx, user_message):
    user_message = user_message.replace('"', '\"')
    user_message = user_message.replace("\'", "")
    try:
        response = create_double_completion(prompts.GOOSE_QUESTION, user_message)
        return response.choices[0].message.content.strip('"')
    except Exception as e:
        return f'Error: {str(e)}'


async def call_goose_attachment(ctx, user_message):
    try:
        attachment = ctx.message.attachments[0]
        if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif']):
            image_url = attachment.url
            response = requests.get(image_url)
            if response.status_code == 200:
                openai_response = create_attachment_completion(prompts.GOOSE_IMAGE_QUESTION, user_message, image_url)
                return openai_response.choices[0].message.content.strip('"')
            else:
                logging.warning(f'Error getting image URL: {str(response.status_code)}')
                return ("Ah, dear seeker of visual delights, alas, there was an error viewing your digital treasure. "
                        "Seek solace in the invisible wonders of the universe, for they hold truths that the eye "
                        "alone cannot perceive.")
        else:
            return ("Ah, dear seeker of visual delights, the contents of your attachment eludes my grasp for I am not "
                    "familiar with its format. Embrace the intangible beauty of the unseen, for sometimes, "
                    "the unseen holds more wisdom than the visible.")
    except Exception as e:
        return f'Error: {str(e)}'
