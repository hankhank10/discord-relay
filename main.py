import os
import requests
import logging

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CUSTOMER_URL = "https://webhook.site/c1e34f4c-f294-463c-a030-394945ef3001"

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    global CUSTOMER_URL

    if message.author == client.user:
        return

    if message.content.startswith("$customer_url="):
        CUSTOMER_URL = message.content.split("=")[1]
        await message.channel.send(f'Customer URL set to {CUSTOMER_URL}')
        logging.info(f"Customer URL set to {CUSTOMER_URL}")

    message_json = {
        'message': {
            'guild': {
                'id': message.guild.id
            },
            'author': {
                'id': message.author.id,
                'name': message.author.name
            },
            'channel': {
                'id': message.channel.id,
                'name': message.channel.name
            },
            'content': {
                'raw': message.content,
                'clean': message.clean_content
            }
        }
    }

    r = requests.post(
        url = CUSTOMER_URL,
        json = message_json
    )

    if r.status_code != 200:
        logging.error (f"Status code {r.status_code} returned")

client.run(TOKEN)
