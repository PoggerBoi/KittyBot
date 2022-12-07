import discord
import openai
import logging

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.CRITICAL)
with open('keys.txt', 'r') as file:
    openai.api_key = file.readline().replace('\n', '')
    discKey = file.readline().replace('\n', '')


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        def is_me(mem):
            if mem == self.user:
                return True

        if is_me(message.author):
            return

        ind = next((i for i, m in enumerate(message.mentions) if is_me(m)), None)
        if ind is not None:
            content = message.content.split(' ', 1)[1]

            response = openai.Completion.create(model="text-curie-001", prompt=content, temperature=0.4,
                                                max_tokens=140)
            logging.critical("sender: " + message.author.name)
            logging.critical("message: " + content)
            logging.critical("response time: " + str(response.response_ms))
            logging.critical(response)
            await message.channel.send(response["choices"][0]["text"])


client = MyClient()
client.run(discKey)

