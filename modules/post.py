import discord
from discord.ext.commands import Bot
from dislash import Option, OptionType, SlashInteraction, has_permissions, InteractionClient
from utils.logging_utils import LoggingUtils


def register_commands_post(slash: InteractionClient, client: Bot):
    @slash.command(
        name=f'message',
        description="Send or edit message in the name of bot",
    )
    @has_permissions(administrator=True)
    async def post(ctx: SlashInteraction, **kwargs):
        pass

    @post.sub_command(
        name='send',
        description='Send message as bot (To get newlines, use escape character \\n)',
        options=[
            Option(
                name='message',
                description='The message to send',
                type=OptionType.STRING,
                required=True
            ),
            Option(
                name='channel',
                description='Text channel to send message in',
                type=OptionType.CHANNEL,
                required=False
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def send_post(ctx: SlashInteraction, message: str, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel
        if isinstance(channel, discord.TextChannel):
            await channel.send(message.replace('\\n', '\n'))
            LoggingUtils.log_to_db('message_sent', user=ctx.author, channel=channel)
            await ctx.send(':thumbsup:', ephemeral=True, delete_after=1)
        else:
            await ctx.reply('You must provide text channel', ephemeral=True, delete_after=2)

    @post.sub_command(
        name='edit',
        description='Edit bot message',
        options=[
            Option(
                name='message_link',
                description='Link to message that you want to edit (Get by R-click on message and "Copy link")',
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
    async def edit_post(ctx: SlashInteraction, message_link: str, message: str):
        try:
            channel_id, message_id = message_link.split('/')[-2:]
            channel_id, message_id = int(channel_id), int(message_id)
            channel: discord.TextChannel = ctx.guild.get_channel(channel_id)
            if isinstance(channel, discord.TextChannel):
                try:
                    msg = channel.get_partial_message(message_id)
                    if msg:
                        try:
                            await msg.edit(content=message.replace('\\n', '\n'))
                            await ctx.reply(':thumbsup:', ephemeral=True, delete_after=1)
                            LoggingUtils.log_to_db('message_edited', user=ctx.author, channel=channel, message=msg)
                        except Exception as e:
                            print(e)
                            await ctx.reply('Could not edit message with provided id', ephemeral=True, delete_after=2)
                    else:
                        await ctx.reply('Could not find message with provided id', ephemeral=True, delete_after=2)
                except Exception as e:
                    print(e)
                    await ctx.reply('Could not find message with provided id', ephemeral=True, delete_after=2)
            else:
                await ctx.reply('You must provide text channel', ephemeral=True, delete_after=2)
        except Exception as e:
            LoggingUtils.logger.error(e)
            await ctx.reply(f"Invalid link provided or something went wrong\n your message was ```{message}```", ephemeral=True)
