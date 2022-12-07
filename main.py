import discord
import openai
import logging
import threading

logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.CRITICAL)
with open('keys.txt', 'r') as file:
    openai.api_key = file.readline().replace('\n', '')
    discKey = file.readline().replace('\n', '')


class MyClient(discord.Client):
    balance = 2000

    def increase_balance(self, inc: int):
        self.balance += inc

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
        if ind is None:
            return

        if len(message.content.split(' ', 1)) == 1:
            return

        content = message.content.split(' ', 1)[1]
        logging.critical("sender: " + message.author.name)
        logging.critical("message: " + content)
        logging.critical("balance: " + str(self.balance))

        if not message.channel.permissions_for(message.mentions[ind]).send_messages:
            print("No permissions to answer a ping")
            return

        if "!balance" in content.lower():
            await message.channel.send("Current token balance: " + str(self.balance))
        elif "image" in content.lower():
            if self.balance < 1000:
                await message.channel.send("Token balance insufficient. Try again later")
                return
            self.balance -= 1000
            response = openai.Image.create(prompt=content, n=1, size="1024x1024")
            logging.critical("response time: " + str(response.response_ms))
            logging.critical(response)
            await message.channel.send(response['data'][0]['url'])
        else:
            if self.balance < 140:
                await message.channel.send("Token balance insufficient. Try again later")
                return
            # cheap - text-curie-001
            # capable - text-davinci-003
            response = openai.Completion.create(model="text-curie-001", prompt=content, temperature=0.6,
                                                max_tokens=140, presence_penalty=1, frequency_penalty=1)
            logging.critical("response time: " + str(response.response_ms))
            logging.critical(response)
            self.balance -= response['usage']['total_tokens']
            await message.channel.send(response["choices"][0]["text"].replace('\n\n', '\n'))


client = MyClient()


def timer_loop():
    client.increase_balance(10)
    threading.Timer(5.0, lambda: timer_loop()).start()


timer_loop()
client.run(discKey)

