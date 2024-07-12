import logging
import config
import copy
from openai import OpenAI

GPT_CLIENT = OpenAI(api_key=config.GPT_KEY, default_headers={"OpenAI-Beta": "assistants=v2"})


async def get_assistant(assistant_id):
    logging.debug("Getting GPT assistant")
    return GPT_CLIENT.beta.assistants.retrieve(assistant_id)


async def create_thread():
    return GPT_CLIENT.beta.threads.create().id


async def delete_thread(thread_id):
    GPT_CLIENT.beta.threads.delete(thread_id)


async def add_single_message(thread_id, message):
    GPT_CLIENT.beta.threads.messages.create(
        thread_id,
        role="user",
        content=message
    )


async def add_multiple_messages(thread_id, message_list):
    for message in message_list:
        GPT_CLIENT.beta.threads.messages.create(
            thread_id,
            role=message.role,
            content=[
                {
                    "type": "text",
                    "text": message.content[0].text.value
                }
            ]
        )


async def get_all_thread_messages(thread_id):
    return GPT_CLIENT.beta.threads.messages.list(thread_id)


###
# Extracts last X amount of messages from a thread
# This includes GPT response messages
# Returns list of alternating gpt responses and user messages
async def get_thread_messages(thread_id, message_num):
    message_list = GPT_CLIENT.beta.threads.messages.list(thread_id)
    return message_list.data[:message_num].reverse()


async def add_attachment_message(thread_id, message, attachment_url):
    GPT_CLIENT.beta.threads.messages.create(
        thread_id,
        role="user",
        content=[
            {
                "type": "text",
                "text": message
            },
            {
                "type": "image_url",
                "image_url": {"url": attachment_url}
            }
        ]
    )


async def run_thread_get_response(thread_id, assistant_id):
    # Automatic polling option
    run = GPT_CLIENT.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    while True:
        status = run.status
        if status == 'queued' or status == 'in_progress':
            logging.info(f"Run is {status}")
        elif run.status == 'completed':
            logging.info(f"Run is {status}")
            message_list = GPT_CLIENT.beta.threads.messages.list(thread_id)
            log_thread_messages(message_list)
            return message_list.data[0].content[0].text.value
        else:
            logging.error(f"Run status is {status}")
            return "There was an error processing your message."


def log_thread_messages(message_list):
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        logging.debug(f"MESSAGE LIST:")
        reverse_data = copy.deepcopy(message_list.data)
        reverse_data.reverse()
        for message in reverse_data:
            logging.debug(f"{message.content[0].text.value}")
