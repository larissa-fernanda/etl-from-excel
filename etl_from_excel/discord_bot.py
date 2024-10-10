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
    """
    Class that represents the Discord bot.
    It will handle the messages and process the attachments.
    """
    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self):
        """
        Function that is called when the bot is ready.
        """
        logger.info(f'Logged in as {self.user}')

    async def on_message(self, message):
        """
        Function that is called when a message is received.
        It will handle the message and process the attachments.

        Args:
            - message (discord.Message): The message that was received.
        """
        logger.info(f'Message from {message.author}: {message.content}')
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            await self.handle_mentions(message)

        if message.attachments:
            await self.process_attachments(message)

        if message.content.lower() == 'ping':
            await message.channel.send('pong')

        if message.content.lower() == 'gato':
            await message.channel.send('https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif')

    async def handle_mentions(self, message):
        """
        Function that is called when the bot is mentioned in a message.
        It will send the instructions or the template.

        Args:
            - message (discord.Message): The message that was received.
        """
        if "instructions" in message.content.lower():
            await self.send_instructions(message.channel)
        elif "template" in message.content.lower():
            await self.send_template(message.channel)

    async def send_instructions(self, channel):
        """
        Function that sends the instructions to the channel.

        Args:
            - channel (discord.TextChannel): The channel to send the instructions.
        """
        instructions = (
            "Instruções de Uso:\n"
            "1. Envie um arquivo no formato .xlsx.\n"
            "2. O bot irá processar o arquivo e enviar os dados para o Airtable.\n"
            "3. Certifique-se de que o arquivo esteja formatado corretamente.\n"
            "4. Você pode definir variáveis de ambiente no formato: KEY=VALUE na mesma mensagem.\n"
            "5. Para receber um template de variáveis de ambiente, envie a mensagem, mencione o bot e mande 'template'.\n"
            "6. Para verificar o status, você pode usar o comando 'ping'.\n"
            "7. Se houver algum erro durante o processamento, o bot irá informar."
        )
        await channel.send(instructions)

    async def send_template(self, channel):
        """
        Function that sends the template to the channel.

        Args:
            - channel (discord.TextChannel): The channel to send the template.
        """
        template = (
            "```"
            "# Nome da aba que será lida (pode deixar em branco)\n"
            "SHEET_NAME=nome_da_aba\n"
            "# Número da linha onde começa o cabeçalho (onde estão os nomes das colunas)\n"
            "HEADER_ROW=13\n"
            "# Nome da(s) coluna(s) que contém a quantidade a ser tratada\n"
            "QUANTITY_COLUMNS=ColunaQuantidade\n"
            "# Nome da(s) coluna(s) que contém a data e hora da transação\n"
            "DATE_COLUMNS=ColunaData/hora\n"
            "# Nome da coluna que será usada como chave primária\n"
            "# Caso não exista, ele pegará a primeira coluna do arquivo\n"
            "PRIMARY_FIELD=ColunaChavePrimária\n"
            "# Nome da(s) coluna(s) que serão usadas para juntar as informações com as que já estão na tabela\n"
            "FIELDS_TO_MERGE_ON=ColunaData/hora,ColunaLocal,ColunaProduto\n"
            "# Nome da(s) coluna(s) que serão selecionadas para serem inseridas na tabela\n"
            "# Caso não exista, ele pegará todas as colunas do arquivo. Só deixar em branco se quiser todas as colunas\n"
            "COLUMNS_TO_SELECT=ColunaData/hora,ColunaLocal,ColunaProduto,ColunaQuantidade,ColunaValor\n"
            "# Colunas que serão usadas para fazer o hash usado para mesclar as informações (equivalente a chave composta de uma tabela)\n"
            "COLUMNS_TO_HASH=ColunaData/hora,ColunaLocal,ColunaProduto\n"
            "# Nome da tabela do Airtable que será usada (se não existir, ele criará uma nova)\n"
            "TABLE_NAME=nome_que_eu_quero_para_minha_nova_tabela_ou_que_já_existe_no_airtable\n"
            "```"
        )
        await channel.send(template)

    async def process_attachments(self, message):
        """
        Function that processes the attachments in the message.
        It will save the enviroment variables and process the xlsx attachments.

        Args:
            - message (discord.Message): The message that was received.
        """
        if message.content:
            for line in message.content.strip().split("\n"):
                if '=' in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip()

        for attachment in message.attachments:
            if attachment.filename.endswith('.xlsx'):
                await self.handle_xlsx_attachment(attachment, message.channel)

    async def handle_xlsx_attachment(self, attachment, channel):
        """
        Function that handles the xlsx attachment.
        It will save the attachment and process it.

        Args:
            - attachment (discord.Attachment): The attachment to be processed.
            - channel (discord.TextChannel): The channel to send the messages.
        """
        temp_path = f"./temp_{attachment.filename}"
        await attachment.save(temp_path)
        logger.info(f'Arquivo {attachment.filename} recebido e salvo em {temp_path}.')
        await channel.send(f'Arquivo {attachment.filename} recebido! Vou tentar salvar! :sweat_smile:')

        try:
            await asyncio.to_thread(etl_main, temp_path)
            logger.info(f'Processamento do arquivo {attachment.filename} concluído com sucesso.')
            await channel.send(f'Processamento do arquivo {attachment.filename} concluído com sucesso aqui do meu lado! Sugiro que verifique lá no Airtable agora! :smile_cat:')

        except Exception as e:
            await self.handle_error(attachment, e, channel)
        
        finally:
            os.remove(temp_path)

    async def handle_error(self, attachment, e, channel):
        """
        Function that handles the error that occurred during the processing of the attachment.
        It will log the error and send a message to the channel.

        Args:
            - attachment (discord.Attachment): The attachment that was being processed.
            - e (Exception): The exception that was raised.
            - channel (discord.TextChannel): The channel to send the messages
        """
        error_message = f"Erro ao processar o arquivo {attachment.filename}: {str(e)}"
        traceback_info = traceback.format_exc()

        prefix_message = "Deu ruim aqui! :tired_face: \n"

        logger.error(f"{error_message}")
        logger.debug(f"{traceback_info}")

        await channel.send(f"{prefix_message}{error_message}")