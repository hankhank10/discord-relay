import os
import requests
import logging

import discord
from dotenv import load_dotenv, set_key

logging.basicConfig(level=logging.INFO)

client = discord.Client(intents=discord.Intents.all())

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CUSTOMER_URL = os.getenv('CUSTOMER_URL')

webhook_suffix = "api/webhook"
heartbeat_suffix = "api/status"

webhook_url = None
heartbeat_url = None

def set_customer_url(url):
    global CUSTOMER_URL
    global webhook_url
    global heartbeat_url
    CUSTOMER_URL = url
    webhook_url = CUSTOMER_URL + webhook_suffix
    heartbeat_url = CUSTOMER_URL + heartbeat_suffix
    set_key(".env", "CUSTOMER_URL", url)

set_customer_url(CUSTOMER_URL)

def check_server_status():
    try:
        r = requests.get(heartbeat_url)
    except:
        logging.error(f"Server is not responding at URL {heartbeat_url}")
        return False
    if r.status_code != 200:
        logging.error(f"Status code {r.status_code} returned from server at URL {heartbeat_url}")
        return False
    logging.info(f"Status code {r.status_code} returned from server at URL {heartbeat_url}")
    return True

@client.event
async def on_ready():
    r = requests.post(
        url=webhook_url,
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
    message_handled = False

    if message.author == client.user:
        return

    if message.content.startswith("$customer_url="):
        url_provided = message.content.split("=")[1]
        set_customer_url(url_provided)
        logging.info(f'Customer URL set to {CUSTOMER_URL}')
        await message.channel.send(f'Customer URL set to {CUSTOMER_URL}')
        message_handled = True

    if message.content.startswith("$ping"):
        await message.channel.send('Pong! (Relay server is up - use $server_status to check game server status)')
        message_handled = True

    if message.content.startswith("$server_status"):
        if check_server_status():
            await message.channel.send(f"Game server is up at url {heartbeat_url}")
        else:
            await message.channel.send(f"Game server is not responding at url {heartbeat_url}")
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
            url = webhook_url,
            json = message_json
        )

        if r.status_code != 200:
            logging.error (f"Status code {r.status_code} returned")



logging.info (f"Customer URL: {CUSTOMER_URL}")
check_server_status()

client.run(TOKEN)

