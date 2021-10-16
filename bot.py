import logging

import discord
from discord import Message
from discord.ext import commands
from dislash import InteractionClient, MessageInteraction, SlashInteraction, has_permissions, OptionType, OptionChoice, \
    Option
from modules.commands import Commands
from utils.bot_helper import prefix
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
    logger.error(error)
    await ctx.channel.send(f'See available slash commands by typing forward-slash and browsing your options')


@slash.command(
    name=f"faculties",
    description="Parent command for faculty actions",
    options=[
        Option(
            name='action',
            description='What action to execute',
            choices=[
                OptionChoice('Generate dropdown selector', 'selector'),
                OptionChoice('Generate stats display', 'stats'),
            ],
            required=True
        )
    ]
)
@has_permissions(administrator=True)
async def faculties(ctx: SlashInteraction, action: str):
    if action == 'selector':
        await ctx.reply(content='Creating selector', ephemeral=True, delete_after=1)
        await Commands.faculty_roles(ctx)
    elif action == 'stats':
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
    name=f'about',
    description='Show info',
)
async def about(context: SlashInteraction):
    await context.send(
        content=f"Developed by @Puupuls for LU Gaming discord",
        delete_after=5,
        ephemeral=True
    )


DB.migrate_db()  # Auto update DB to newest level

client.run('')

