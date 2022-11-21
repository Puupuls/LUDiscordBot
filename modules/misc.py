from discord.ext.commands import Bot
from dislash import SlashInteraction, InteractionClient
from utils.database import DB
from utils.logging_utils import LoggingUtils


def register_commands_misc(slash: InteractionClient, client: Bot):
    @slash.command(
        name=f'about',
        description='Show info',
    )
    async def about(context: SlashInteraction):
        await context.send(
            content=f"Developed by @Puupuls for LU Gaming discord\n[Github](https://github.com/Puupuls/LUDiscordBot)",
            delete_after=5,
            ephemeral=True
        )

    @slash.command(
        name=f'set_log_channel',
        description='Set current channel as bots log channel, server can have only one log channel',
    )
    async def slc(ctx: SlashInteraction):
        DB.set_setting('log_channel', ctx.channel.id)
        await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
        await LoggingUtils.log_to_db(event_name='set_log_channel', user=ctx.author, channel=ctx.channel)
        await ctx.reply(':thumbsup:', ephemeral=True)