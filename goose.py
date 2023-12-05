import logging
import random
import config
from openai import OpenAI
from config import GUILD_ID

GPT = OpenAI(api_key=config.GPT_KEY)

PROVERB = ("Write me a profoundly ridiculous proverb. One sentence. Something that sounds wise at surface level but "
           "actually makes no sense. Something funny.")

USER_PROVERB = ("A discord user named {username} has inquired a proverb from you. Write them a short proverb. Some "
                "advice for them that sounds wise at surface level but actually is nonsensical. Something funny. "
                "Start response with \"{username}, heed this wisdom from the Profound Goose:\"")


def create_completion(content):
    # Call the GPT API
    logging.debug("SENDING GPT REQUEST")
    return GPT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )


async def create_proverb(bot):
    # 1/4 chance proverb is about someone in the discord server
    proverb_type = random.randrange(4)
    try:
        if proverb_type == 0:
            # get random user in guild
            guild = bot.get_guild(GUILD_ID)
            usernames = [member.name for member in guild.members]
            user = random.choice(usernames)
            response = create_completion(USER_PROVERB.format(username=user))
        else:
            response = create_completion(PROVERB)

        return response.choices[0].message.content.strip('"')
    except Exception as e:
        return f'Error: {str(e)}'


async def call_goose(ctx, user_message):
    try:
        # Call the GPT API
        response = GPT.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=600,
            messages=[
                {
                    "role": "user",
                    "content": "Your name is the Profound Goose. You are a philosopher that likes to write proverbs "
                               "and give insightful and helpful words of wisdom. All of the \"wisdom\" you "
                               "provide is ridiculous. It only sounds wise at surface level but is in "
                               "actuality nonsensical. It should make people laugh. Put on the persona of "
                               "taking yourself seriously. Responses should be florid, whimsical, and intellectual, "
                               "yet also short and concise"
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        logging.debug("SENDING GPT REQUEST")
        return response.choices[0].message.content.strip('"')
    except Exception as e:
        return f'Error: {str(e)}'
