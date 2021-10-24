from datetime import datetime, timedelta

from discord.ext.commands import Bot
from dislash import Option, OptionType, SlashInteraction, InteractionClient
from pytimeparse.timeparse import timeparse

from utils.database import DB
from utils.logging_utils import LoggingUtils


def register_commands_events(slash: InteractionClient, client: Bot):
    @slash.command(
        name='event',
        description='Event command base'
    )
    async def event(ctx: SlashInteraction, **kwargs):
        pass

    @event.sub_command(
        name='create',
        description='Create a private event (you will need approval of admins, once you have submitted needed info). One user can have ony one event at a time',
        options=[
            Option(
                name='name',
                description='What is your event called',
                type=OptionType.STRING
            ),
            Option(
                name='description',
                description='What is your event about',
                type=OptionType.STRING
            ),
            Option(
                name='start',
                description='When will your event start in form YYYY/MM/DD HH:MM',
                type=OptionType.STRING
            ),
            Option(
                name='duration',
                description='How long will it go for',
                type=OptionType.STRING
            ),
        ]
    )
    async def event_create(ctx: SlashInteraction, name: str, description: str, start: str, duration: str):
        try:
            start = datetime.strptime(start, '%Y/%m/%d %H:%M')
            try:
                duration = timeparse(duration)
                try:
                    is_admin = ctx.author.permissions_in(ctx.channel).administrator
                    msg_id = None

                    with DB.cursor() as cur:
                        cur.execute("INSERT INTO events "
                                    "(user_id, name, description, is_confirmed, is_rejected, reviewer_id, confirmation_message_id, start_time, end_time) VALUES "
                                    "(?,?,?,?,?,?,?,?,?)",
                                    (
                                        ctx.author.id,
                                        name,
                                        description,
                                        is_admin,
                                        False,
                                        None,
                                        msg_id,
                                        start,
                                        start + duration
                                    ))
                except Exception as e:
                    LoggingUtils.logger.error(e)
                    await ctx.reply('Neizdevās veikt šo darbību', ephemeral=True, delete_after=1)
            except:
                await ctx.reply('Nepareizs ilguma formāts', ephemeral=True, delete_after=1)
        except:
            await ctx.reply('Nepareizs sākuma laika formāts', ephemeral=True, delete_after=1)
