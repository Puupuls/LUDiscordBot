from datetime import datetime, timedelta

import discord
from discord.ext.commands import Bot
from dislash import SlashInteraction, InteractionClient, has_permissions, Option, OptionType
from utils.database import DB
from utils.logging_utils import LoggingUtils


def register_commands_moderation(slash: InteractionClient, client: Bot):
    @slash.command(
        name=f'warn',
        description='Give user a warning',
        options=[
            Option(
                name='user',
                description='Target user',
                type=OptionType.USER,
                required=True
            ),
            Option(
                name='reason',
                description='Why are you warning this user',
                type=OptionType.STRING,
                required=True
            ),
            Option(
                name='create_anchor',
                description='Send a message in this chat and link to it (default=True)',
                type=OptionType.BOOLEAN,
                required=False
            )
        ]
    )
    @has_permissions(kick_members=True)
    async def warn(ctx: SlashInteraction, user: discord.user, reason: str, create_anchor: bool = True):
        try:
            await user.send(f'Kāds no administrācijas izteica tev brīdinājumu (Someone has given you a warning)\nIemesls: `{reason}`')
        except Exception as e:
            LoggingUtils.logger.info("This is okay!")
            LoggingUtils.logger.error(e)

        msg = None
        if create_anchor:
            msg: discord.Message = await ctx.channel.send(f'{user.mention} Tev tiek izteikts brīdinājums par `{reason}`')
        await ctx.reply(':thumbsup:', ephemeral=True)
        with DB.cursor() as cur:
            cur.execute("INSERT INTO mod_log "
                        "(user_id, moderator_id, action, bot_message_link, reason, timestamp) VALUES "
                        "(?, ?, ?, ?, ?, ?)",
                        (
                            user.id,
                            ctx.author.id,
                            'WARN',
                            msg.jump_url if msg else '',
                            reason,
                            datetime.now()
                        ))
        LoggingUtils.log_to_db(
            event_name='issued_warning',
            user=ctx.author,
            message=msg if msg else None,
            channel=msg.channel if msg else None,
            target_user=user,
            other_data={'reason': reason}
        )
        await LoggingUtils.log_to_discord(
            ctx,
            f"ISSUED WARNING",
            LoggingUtils.LogLevels.WARN,
            issuer=ctx.author.mention,
            target=user.mention,
            reason=reason,
            location=f"[click to open]({msg.jump_url})" if msg else ctx.channel.mention
        )

    # @slash.command(
    #     name=f'kick',
    #     description='Kick user',
    # )
    # @has_permissions(kick_members=True)
    # async def kick(ctx: SlashInteraction):
    #     DB.set_setting('log_channel', ctx.channel.id)
    #     await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
    #     await ctx.reply(':thumbsup:', ephemeral=True)
    #
    # @slash.command(
    #     name=f'ban',
    #     description='Ban user',
    # )
    # @has_permissions(ban_members=True)
    # async def ban(ctx: SlashInteraction):
    #     DB.set_setting('log_channel', ctx.channel.id)
    #     await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
    #     await ctx.reply(':thumbsup:', ephemeral=True)
    #
    # @slash.command(
    #     name=f'unban',
    #     description='Unban user',
    # )
    # @has_permissions(ban_members=True)
    # async def unban(ctx: SlashInteraction):
    #     DB.set_setting('log_channel', ctx.channel.id)
    #     await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
    #     await ctx.reply(':thumbsup:', ephemeral=True)

    # @slash.command(
    #     name=f'mute',
    #     description='Mute user',
    # )
    # @has_permissions(manage_messages=True)
    # async def mute(ctx: SlashInteraction):
    #     DB.set_setting('log_channel', ctx.channel.id)
    #     await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
    #     await ctx.reply(':thumbsup:', ephemeral=True)
    #
    # @slash.command(
    #     name=f'unmute',
    #     description='Unmute user',
    # )
    # @has_permissions(manage_messages=True)
    # async def unmute(ctx: SlashInteraction):
    #     DB.set_setting('log_channel', ctx.channel.id)
    #     await LoggingUtils.log_to_discord(ctx, 'Set this channel as logging channel')
    #     await ctx.reply(':thumbsup:', ephemeral=True)

    @slash.command(
        name=f'incident_history',
        description='See users history',
        options=[
            Option(
                name='user',
                description='Target user',
                type=OptionType.USER,
                required=True
            )
        ]
    )
    @has_permissions(manage_messages=True)
    async def history(ctx: SlashInteraction, user: discord.User):
        hist = ''
        with DB.cursor() as cur:
            cur.execute("Select * from mod_log where user_id = ?", (user.id,))
            for row in cur:
                hist += f"[{row['action']}]({row['bot_message_link']}) " \
                        f"on `{row['timestamp']}` " \
                        f"by {ctx.guild.get_member(row['moderator_id']).mention} " \
                        f"for `{row['reason']}`\n\n"
        if not hist:
            hist = 'This user has done nothing wrong'
        await ctx.reply(hist, ephemeral=True)

    @slash.command(
        name=f'recent_incidents',
        description='See recent incidents',
    )
    @has_permissions(manage_messages=True)
    async def recent(ctx: SlashInteraction):
        hist = ''
        with DB.cursor() as cur:
            cur.execute("Select * from mod_log where timestamp > ?", (datetime.now() - timedelta(days=7),))
            for row in cur:
                try:
                    member = ctx.guild.get_member(row['user_id'])
                except:
                    member = None
                hist += f"[{row['action']}]({row['bot_message_link']}) {member.mention if member else '#removed_user'}" \
                        f"on `{row['timestamp']}` " \
                        f"by {ctx.guild.get_member(row['moderator_id']).mention} " \
                        f"for **{row['reason']}**\n\n"
        if not hist:
            hist = 'No user has committed crimes in last week'
        await ctx.reply(hist, ephemeral=True)