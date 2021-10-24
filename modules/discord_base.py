import logging
import discord
from discord.ext import commands
from dislash import InteractionClient
from ENV import GUILDS, OWNER
from utils.bot_helper import BotHelper
from utils.logging_utils import LoggingUtils


def init_discord():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.ERROR)

    LoggingUtils.init('bot')
    logger = LoggingUtils.logger

    intents = discord.Intents.default()
    intents.members = True

    client = commands.Bot(
        command_prefix=BotHelper.prefix(),
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=''
        ),
        owner_id=OWNER,
        intents=intents,
        help_command=None,
        case_insensitive=True,
        strip_after_prefix=True
    )

    slash = InteractionClient(client, test_guilds=GUILDS)

    return slash, client
