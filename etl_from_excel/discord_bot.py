import os
import asyncio
import traceback
import discord
from loguru import logger
from etl import main as etl_main

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self):
        logger.info(f'Logged in as {self.user}')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')
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
                    logger.info(f'Arquivo {attachment.filename} recebido e salvo em {temp_path}.')
                    await message.channel.send(f'Arquivo {attachment.filename} recebido! Vou tentar salvar! :sweat_smile:')

                    try:
                        await asyncio.to_thread(etl_main, temp_path)
                        logger.info(f'Processamento do arquivo {attachment.filename} concluído com sucesso.')
                        await message.channel.send(f'Processamento do arquivo {attachment.filename} concluído com sucesso aqui do meu lado! Sugiro que verifique lá no Airtable agora! :smile_cat:')

                    except Exception as e:
                        error_message = f"Erro ao processar o arquivo {attachment.filename}: {str(e)}"
                        traceback_info = traceback.format_exc()

                        prefix_message = "Deu ruim aqui! :tired_face: \n"

                        logger.error(f"{error_message}")
                        logger.debug(f"{traceback_info}")

                        await message.channel.send(f"{prefix_message}{error_message}")

                    
                    finally:
                        os.remove(temp_path)

        if message.content.lower() == 'ping':
            await message.channel.send('pong')

