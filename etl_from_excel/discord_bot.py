import asyncio
import discord
import os
from etl import main as etl_main

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return

        if message.attachments:
            if message.content:
                for line in message.content.strip().split("\n"):
                    if '=' in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value.strip()

            for attachment in message.attachments:
                if attachment.filename.endswith('.xlsx'):
                    temp_path = f"./temp_{attachment.filename}"
                    await attachment.save(temp_path)
                    print(f'Arquivo {attachment.filename} recebido e salvo em {temp_path}.')

                    await asyncio.to_thread(etl_main, temp_path)

                    os.remove(temp_path)

        if message.content.lower() == 'ping':
            await message.channel.send('pong')

