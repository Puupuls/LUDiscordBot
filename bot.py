from discord import Message
from dislash import MessageInteraction, SlashInteraction
from modules.discord_base import init_discord, BOT_TOKEN
from modules.faculties import on_faculty_role, register_commands_faculty
from modules.post import register_commands_post
from modules.rules import register_commands_rule
from utils.database import DB
from utils.logging_utils import LoggingUtils

slash, client = init_discord()
register_commands_faculty(slash, client)
register_commands_rule(slash, client)
register_commands_post(slash, client)


@client.event
async def on_ready():
    pass


@client.event
async def on_command_error(ctx, error):
    LoggingUtils.logger.error(error)
    await ctx.channel.send(f'See available slash commands by typing forward-slash and browsing your options')


@client.event
async def on_slash_command_error(ctx: SlashInteraction, error):
    LoggingUtils.logger.error(error)
    await ctx.reply(f'See available slash commands by typing forward-slash and browsing your options', ephemeral=True, delete_after=2)


@client.event
async def on_dropdown(inter: MessageInteraction):
    if inter.component.custom_id == 'facultiesSelect':
        await on_faculty_role(inter, inter.component.selected_options[0])


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
    name=f'set_log_channel',
    description='Set curren channel as bots log channel, server can have only one log channel',
)
async def about(ctx: SlashInteraction):
    DB.set_setting('log_channel', ctx.channel.id)
    await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
    await ctx.reply(':thumbsup:', ephemeral=True)


DB.migrate_db()  # Auto update DB to newest level
client.run(BOT_TOKEN)
