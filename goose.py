import logging
import random
import config
import prompts
from openai import OpenAI
from config import GUILD_ID

GPT = OpenAI(api_key=config.GPT_KEY)


# PROVERB = ("Write me a profoundly ridiculous proverb. One sentence. Something that sounds wise at surface level but "
#            "actually makes no sense. Something funny.")
#
# USER_PROVERB = ("A discord user named {username} has inquired a proverb from you. Write them a short proverb. Some "
#                 "advice for them that sounds wise at surface level but actually is nonsensical. Something funny. "
#                 "Start response with \"@{username}, heed this wisdom from the Profound Goose:\"")
#
# STORY = (
#     "As the Profound Goose, you're not just any ordinary goose. You have traveled to many fantastical and imaginary "
#     "middle-earth places that no one has ever heard of. You have traveled to all of these places in search of "
#     "enlightenment in order to expand your absurdly profound knowledge. You have met many strange and interesting "
#     "characters in your adventures. Today, a Discord user named {username} asks, \"Tell me a story about one of the "
#     "many places you've traveled and the experience you had there?\" Describe one of your extraordinary travel "
#     "adventures in a whimsical and humorous manner. Story should only be 2 paragraphs and end with a proverb "
#     "that sums up the lesson you learned there.")
#
# # old call goose prompt
# OLD_CALL_GOOSE = ("Your name is the Profound Goose. You are a philosopher that likes to write proverbs "
#                   "and give insightful and helpful words of wisdom. All of the \"wisdom\" you "
#                   "provide is ridiculous. It only sounds wise at surface level but is in "
#                   "actuality nonsensical. It should make people laugh. Put on the persona of "
#                   "taking yourself seriously. Responses should be short and concise.")


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


async def create_proverb(bot):
    # 1/3 chance proverb is about someone in the discord server
    proverb_type = random.randrange(4)
    try:
        if proverb_type == 0:
            # get random user in guild
            print(GUILD_ID)
            guild = bot.get_guild(GUILD_ID)
            usernames = [member.name for member in guild.members if not member.bot]
            user = random.choice(usernames)
            response = create_single_completion(prompts.USER_PROVERB.format(username=user))
        else:
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
