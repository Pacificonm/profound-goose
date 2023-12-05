import logging

import config
from openai import OpenAI

GPT = OpenAI(api_key=config.GPT_KEY)


async def create_proverb():
    try:
        # Call the GPT API
        response = GPT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Write me a profoundly ridiculous proverb. One sentence. Something that sounds "
                               "wise at surface level but actually makes so sense. Something funny."
                }
            ]
        )

        logging.debug("SENDING GPT REQUEST")
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
