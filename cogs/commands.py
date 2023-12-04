import datetime
import logging

from discord.ext import commands

from gpt_setup import GPT

COMMAND_MAX = 5  # Maximum number of executions
COOLDOWN_TIME = 86400  # Time in seconds (86400 secs in a day)


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_tracker = {}  # Dictionary that stores user_id: (count, last_reset_time)

    # This command is limited to MAX numbers of executions per day per user
    @commands.command(name="heyGoose")
    async def ask_goose(self, ctx, *args):
        user_id = ctx.author.id
        message = ''.join(args)

        if user_id in self.command_tracker:
            count, last_reset_time = self.command_tracker[user_id]
            seconds_elapsed = (datetime.datetime.now() - last_reset_time).total_seconds()

            if seconds_elapsed >= COOLDOWN_TIME:
                # After cooldown time reset count
                logging.info(f"{user_id} has asked 1 question")
                self.command_tracker[user_id] = (1, datetime.datetime.now())
                await call_gpt(ctx, message)
            elif count < COMMAND_MAX:
                logging.info(f"{user_id} has asked {count + 1} questions")
                self.command_tracker[user_id] = (count + 1, last_reset_time)
                await call_gpt(ctx, message)
            else:
                hh_mm_ss = str(datetime.timedelta(seconds=seconds_elapsed))
                await ctx.send(f"Dear seeker of knowledge, you have reached the boundary of questions that you may "
                               f"ask of me. Return in {hh_mm_ss} for more profound ponderings.")
        else:
            # First time user
            logging.info(f"{user_id} has asked 1 question")
            self.command_tracker[user_id] = (1, datetime.datetime.now())
            await call_gpt(ctx, message)


async def setup(bot):
    await bot.add_cog(CommandCog(bot))


# TODO: Implement GPT assistant in order to have conversation threads

async def call_gpt(ctx, user_message):
    try:
        # Call the GPT API
        response = GPT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Your name is the Profound Goose. You are a philosopher that likes to write proverbs "
                               "and give insightful and helpful words of wisdom. All of the \"wisdom\" you "
                               "provide is ridiculous. It only sounds wise at surface level but is in "
                               "actuality nonsensical. It should make people laugh. Put on the persona of "
                               "taking yourself seriously."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        logging.debug("SENDING GPT REQUEST")
        # Send the response back as a Discord message
        await ctx.send(response.choices[0].message.content.strip('"'))
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')
