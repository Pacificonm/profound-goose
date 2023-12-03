from discord.ext import commands, tasks
from gpt_setup import GPT


class TaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(hours=24)
    async def wisdom_message(self):
        channel = self.bot.get_channel(1179978297560535163)  # Replace with your channel ID
        try:
            # Call the OpenAI API
            response = GPT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "Write me a profoundly ridiculous proverb. One sentence. Something that sounds wise at surface level but actually makes so sense. Something funny."
                    }
                ]
            )

            print("SENDING GPT REQUEST")
            # Send the response back as a Discord message
            await channel.send(response.choices[0].message.content.strip('"'))
        except Exception as e:
            await channel.send(f'Error: {str(e)}')

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.wisdom_message.start()


async def setup(bot):
    await bot.add_cog(TaskCog(bot))
