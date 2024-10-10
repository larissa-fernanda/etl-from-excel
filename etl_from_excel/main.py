import os
from dotenv import load_dotenv
from .discord_bot import MyClient

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client = MyClient()
client.run(DISCORD_BOT_TOKEN)