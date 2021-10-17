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


@client.event
async def on_slash_command_error(ctx: SlashInteraction, error):
    logger.error(error)
    print(error)
    await ctx.reply(f'See available slash commands by typing forward-slash and browsing your options', ephemeral=True, delete_after=2)

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
            required=True,
            type=OptionType.STRING
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


@slash.command(
    name=f'message',
)
async def post(ctx: SlashInteraction, **kwargs):
    pass


@post.sub_command(
    name='send',
    description='Send message as bot (To get newlines, use escape character \\n)',
    options=[
        Option(
            name='channel',
            description='Text channel to send message in',
            type=OptionType.CHANNEL,
            required=True
        ),
        Option(
            name='message',
            description='The message to send',
            type=OptionType.STRING,
            required=True
        ),
    ]
)
@has_permissions(administrator=True)
async def send_post(ctx: SlashInteraction, channel: discord.TextChannel, message: str):
    await Commands.send_post(ctx, channel, message)


@post.sub_command(
    name='edit',
    description='Edit bot message',
    options=[
        Option(
            name='channel',
            description='Text channel to send message in',
            type=OptionType.CHANNEL,
            required=True
        ),
        Option(
            name='message_id',
            description='Message to edit',
                type=OptionType.STRING,
            required=True
        ),
        Option(
            name='message',
            description='New message text',
            type=OptionType.STRING,
            required=True
        ),
    ]
)
@has_permissions(administrator=True)
async def edit_post(ctx: SlashInteraction, channel: discord.TextChannel, message_id: str, message: str):
    await Commands.edit_post(ctx, channel, int(message_id), message)


@slash.command(
    name='rule'
)
async def rule(ctx, **kwargs):
    pass


@rule.sub_command(
    name='create_message',
    description='Create rules message in current chat',
)
async def rule_message(ctx: SlashInteraction):
    await Commands.rules_message(ctx)


@rule.sub_command(
    name='add',
    description='Add new rule',
    options=[
        Option(
            name='message',
            description='The message to send',
            type=OptionType.STRING,
            required=True
        ),
    ]
)
async def add_rule(ctx: SlashInteraction, message: str):
    await Commands.rules_add(ctx, message)


@rule.sub_command(
    name='remove',
    description='Remove rule',
    options=[
        Option(
            name='id',
            description='Rule order id',
            type=OptionType.INTEGER,
            required=True
        ),
    ]
)
async def remove_rule(ctx: SlashInteraction, id: int):
    await Commands.rules_remove(ctx, id)


@rule.sub_command(
    name='reposition',
    description='Change rules position in list',
    options=[
        Option(
            name='id',
            description='Rule order id',
            type=OptionType.INTEGER,
            required=True
        ),
        Option(
            name='new_pos',
            description='New position of role in list',
            type=OptionType.INTEGER,
            required=True
        ),
    ]
)
async def move_rule(ctx: SlashInteraction, id: int, new_pos: int):
    await Commands.rules_reorder(ctx, id, new_pos)


DB.migrate_db()  # Auto update DB to newest level

client.run('')

