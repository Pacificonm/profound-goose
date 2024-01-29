import logging
import random
import config
import prompts
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
def create_double_completion(instruction_prompt, prompt):
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
                "content": prompt
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
