import logging

import discord
from discord import Client, Message

from modules.message_handler import MessageHandler
from utils.logging_utils import LoggingUtils

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)

LoggingUtils.init('bot')

intents = discord.Intents.default()
intents.members = True

#  Using Client not extensions.bot will grant lower level access and more flexibility in future if we would need it
client = Client(
    status=discord.Status.online,
    activity=discord.Activity(
        type=discord.ActivityType.playing,
        name=''
    ),
    intents=intents
)


@client.event
async def on_ready():
    pass


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    await MessageHandler.handle(message, client)

client.run('')