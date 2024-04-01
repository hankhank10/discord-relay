import os
import requests
import logging

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CUSTOMER_URL = os.getenv('CUSTOMER_URL') + "api/webhook"
HEARTBEAT_URL = os.getenv('CUSTOMER_URL') + "api/status"

logging.basicConfig(level=logging.INFO)

client = discord.Client(intents=discord.Intents.all())

def check_server_status():
    r = requests.get(HEARTBEAT_URL)
    if r.status_code != 200:
        logging.error(f"Status code {r.status_code} returned from server at URL {HEARTBEAT_URL}")
        return False
    logging.info(f"Status code {r.status_code} returned from server at URL {HEARTBEAT_URL}")
    return True


@client.event
async def on_ready():
    r = requests.post(
        url=CUSTOMER_URL,
        json={
            'event': 'connected_to_guild',
            'guild': {
                'id': client.guilds[0].id
            },
            'user': {
                'id': client.user.id,
                'name': client.user.name
            }
        }
    )
    logging.info(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    global CUSTOMER_URL
    message_handled = False

    if message.author == client.user:
        return

    if message.content.startswith("$customer_url="):
        CUSTOMER_URL = message.content.split("=")[1] + "api/webhook"
        await message.channel.send(f'Customer URL set to {CUSTOMER_URL}')
        message_handled = True

    if message.content.startswith("$server_status"):
        if check_server_status():
            await message.channel.send(f"Server is up at url {HEARTBEAT_URL}")
        else:
            await message.channel.send(f"Server is not responding at url {HEARTBEAT_URL}")
        message_handled = True

    message_json = {
        'event': 'message',
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

    print(message.content)

    if not message_handled:
        r = requests.post(
            url = CUSTOMER_URL,
            json = message_json
        )

        if r.status_code != 200:
            logging.error (f"Status code {r.status_code} returned")

logging.info (f"Customer URL: {CUSTOMER_URL}")
check_server_status()

client.run(TOKEN)

