import dislash
from discord import Message
from dislash import MessageInteraction, SlashInteraction

from ENV import BOT_TOKEN
from modules.discord_base import init_discord
from modules.faculties import on_faculty_role, register_commands_faculty
from modules.misc import register_commands_misc
from modules.moderation import register_commands_moderation
from modules.post import register_commands_post
from modules.rules import register_commands_rule
from utils.database import DB
from utils.logging_utils import LoggingUtils

slash, client = init_discord()
register_commands_misc(slash, client)
register_commands_faculty(slash, client)
register_commands_rule(slash, client)
register_commands_post(slash, client)
register_commands_moderation(slash, client)
# register_commands_events(slash, client)  # Not working, need more concepts about how to implement nicely


@client.event
async def on_command_error(ctx, error):
    LoggingUtils.logger.error(error)


@client.event
async def on_slash_command_error(ctx: SlashInteraction, error):
    LoggingUtils.logger.error(error)
    if error == dislash.MissingPermissions:
        await ctx.reply("You do not have sufficient permissions to use that command", ephemeral=True, delete_after=2)
    else:
        await ctx.reply(f'See available slash commands by typing forward-slash and browsing your options', ephemeral=True, delete_after=2)


@client.event
async def on_dropdown(inter: MessageInteraction):
    if inter.component.custom_id == 'facultiesSelect':
        await on_faculty_role(inter, inter.component.selected_options[0])


@client.event
async def on_message_delete(message: Message):
    with DB.cursor() as cur:
        cur.execute("DELETE FROM messages WHERE message=?", (message.id,))


DB.migrate_db()  # Auto update DB to newest level
client.run(BOT_TOKEN)
