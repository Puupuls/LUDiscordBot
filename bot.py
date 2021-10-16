import logging
import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Context, has_permissions
from dislash import InteractionClient, MessageInteraction

from modules.commands import Commands
from utils.bot_helper import prefix, set_prefix
from utils.database import DB
from utils.logging_utils import LoggingUtils

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)

LoggingUtils.init('bot')
logger = LoggingUtils.logger

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(
    command_prefix=prefix,
    status=discord.Status.online,
    activity=discord.Activity(
        type=discord.ActivityType.playing,
        name=''
    ),
    owner_id=240041172125483010,
    intents=intents,
    help_command=None,
    strip_after_prefix=True
)
slash = InteractionClient(client)
guilds = [824209921444544533, 755035407380643971]


@client.event
async def on_ready():
    pass


@client.event
async def on_command_error(ctx, error):
    logger.error(error)
    await ctx.channel.send(f'{error}\nSee `{ctx.prefix}help` for more info')


@client.command(
    name='prefix',
    description='Change command prefix',
    usage='new_prefix',
)
@has_permissions(administrator=True)
async def prefix(ctx, new_prefix: str = ''):
    await Commands.prefix(ctx, new_prefix)


@client.command(
    name='facultyRoles',
    description='Create faculty role selection message',
    usage='',
)
@has_permissions(administrator=True)
async def faculty_roles(ctx):
    await Commands.faculty_roles(ctx)


@client.command(
    name='facultyStats',
    description='Create faculty role statistics message',
    usage='',
)
@has_permissions(administrator=True)
async def faculty_stats(ctx):
    await Commands.faculty_stats(ctx)


@client.event
async def on_dropdown(inter: MessageInteraction):
    if inter.component.custom_id == 'facultiesSelect':
        await Commands.on_faculty_role(inter, inter.component.selected_options[0])


@client.event
async def on_message_delete(message: Message):
    with DB.cursor() as cur:
        cur.execute("DELETE FROM messages WHERE message=?", (message.id,))


@client.command(
    name='help',
    description='Show commands and usages',
    usage='',
    hidden=True
)
async def help(context: Context):
    await Commands.help(context)


@client.command(
    name='cleanDB',
    description='',
    usage='',
    hidden=True
)
@has_permissions(administrator=True)
async def help(context: Context):
    DB.clean_db()

client.run('')

