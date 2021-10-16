import logging
import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Context, has_permissions
from dislash import InteractionClient, MessageInteraction, SlashInteraction
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
    case_insensitive=True,
    strip_after_prefix=True
)
guilds = [824209921444544533, 755035407380643971]
slash = InteractionClient(client, test_guilds=guilds)


@client.event
async def on_ready():
    pass


@client.event
async def on_command_error(ctx, error):
    await ctx.channel.send(f'See available slash commands, my commands are prefixed with "lu_"')


@client.command(
    name='prefix',
    description='Change command prefix',
    usage='new_prefix',
)
@has_permissions(administrator=True)
async def prefix(ctx, new_prefix: str = ''):
    await Commands.prefix(ctx, new_prefix)


@slash.command(
    name='lu_faculty_select',
    description='Create faculty role selection message',
)
@has_permissions(administrator=True)
async def faculty_roles(ctx: SlashInteraction):
    await ctx.reply(content='Creating selector', ephemeral=True, delete_after=1)
    await Commands.faculty_roles(ctx)


@slash.command(
    name='lu_faculty_stats',
    description='Create faculty role statistics message',
)
@has_permissions(administrator=True)
async def faculty_stats(ctx: SlashInteraction):
    await ctx.reply(content='Creating stats display', ephemeral=True, delete_after=1)
    await Commands.faculty_stats(ctx)


@client.event
async def on_dropdown(inter: MessageInteraction):
    if inter.component.custom_id == 'facultiesSelect':
        await Commands.on_faculty_role(inter, inter.component.selected_options[0])


@client.event
async def on_message_delete(message: Message):
    with DB.cursor() as cur:
        cur.execute("DELETE FROM messages WHERE message=?", (message.id,))


@slash.command(
    name='lu_help',
    description='Show info',
)
async def help(context: SlashInteraction):
    await context.send(
        content="This plugin uses slash commands prefixed with \"lu_\"\nDeveloped by @Puupuls",
        delete_after=5,
        ephemeral=True
    )


DB.migrate_db()  # Auto update DB to newest level

client.run('')

