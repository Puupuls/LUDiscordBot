from datetime import datetime

from discord.ext.commands import Bot
from dislash import Option, OptionType, SlashInteraction, InteractionClient


def register_commands_events(slash: InteractionClient, client: Bot):
    @slash.command(
        name='event',
        description='Event command base'
    )
    async def event(ctx: SlashInteraction, **kwargs):
        pass

    @event.sub_command(
        name='create',
        description='Create a private event (you will need approval of admins, once you have submitted needed info)',
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
                description='How long will it go for (2 hours, 1 day, etc)',
                type=OptionType.STRING
            ),
        ]
    )
    async def event_create(ctx: SlashInteraction, name: str, description: str, start: str, duration: str):
        # user_id
        # name
        # description
        # is_confirmed
        # is_rejected
        # reviewer_id
        # confirmation_message_id
        # start_time datetime
        # end_time datetime
        try:
            start = datetime.strptime(start, '%Y/%m/%d %H:%M')
        except:
            await ctx.reply('Nepareizs sākuma laika formāts')
