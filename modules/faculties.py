from datetime import datetime, timedelta

import discord
from discord import Permissions, PartialEmoji, Embed
from discord.ext.commands import Bot
from dislash import SlashInteraction, MessageInteraction, SelectOption, SelectMenu, has_permissions, InteractionClient, \
    Option, OptionType
from utils.bot_helper import BotHelper
from utils.database import DB
from utils.logging_utils import LoggingUtils


def register_commands_faculty(slash: InteractionClient, client: Bot):
    @slash.command(
        name=f"faculties",
        description="Parent command for faculty actions",
    )
    async def faculties(ctx: SlashInteraction):
        pass

    @faculties.sub_command(
        name='selector',
        description='Create faculty role selector',
    )
    @has_permissions(administrator=True)
    async def faculties_selector(ctx: SlashInteraction):
        await ctx.reply(content='Creating selector', ephemeral=True, delete_after=1)
        options = []
        with DB.cursor() as cur:
            cur.execute("SELECT * FROM faculties order by title")
            for row in cur.fetchall():
                emoji = None
                try:
                    for e in ctx.guild.emojis:
                        if e.name.lower() == row['icon'].lower():
                            emoji = e
                except:
                    pass
                options.append(
                    SelectOption(
                        row['title'].strip(),
                        row['role'],
                        emoji=PartialEmoji(
                            name=emoji.name if emoji else None,
                            id=emoji.id if emoji else None
                        ) if emoji else None
                    )
                )

        options = SelectMenu(
            options=options,
            custom_id='facultiesSelect',
            max_values=1,
            placeholder='Lūdzu izvēlies savu fakultāti'
        )
        msg = await ctx.channel.send(
            content="Izvēlies savu fakultāti (ja esi pārstāvējis vairākas, izvēlies pēdējo vai arī to, kurai jūties vairāk piederīgs)",
            components=[options]
        )
        with DB.cursor() as cur:
            cur.execute("INSERT INTO messages (channel, message, type) VALUES (?, ?, ?)",
                        (msg.channel.id, msg.id, 'facultiesSelect'))

        LoggingUtils.log_to_db('faculties_selector_created', user=ctx.author)

    @faculties.sub_command(
        name='stats',
        description='Create faculty member count display',
    )
    @has_permissions(administrator=True)
    async def faculties_selector(ctx: SlashInteraction):
        await ctx.reply(content='Creating stats display', ephemeral=True, delete_after=1)
        embed = Embed(color=0xeaaa00)
        embed.title = 'Šobrīdējais fakultāšu pārstāvju skaits serverī'
        msg = await ctx.channel.send(embed=embed)
        with DB.cursor() as cur:
            cur.execute("INSERT INTO messages (channel, message, type) VALUES (?, ?, ?)",
                        (msg.channel.id, msg.id, 'facultiesStats'))
        LoggingUtils.log_to_db('faculties_stats_created', user=ctx.author)
        await update_faculty_stats(ctx)

    @faculties.sub_command(
        name='lockuser',
        description='Set user\'s faculty and do not allow them to change it.',
        options=[
            Option(
                name='user',
                description='What user shall get locked',
                type=OptionType.USER,
                required=True
            ),
            Option(
                name='faculty',
                description='What faculty is user part of',
                type=OptionType.ROLE,
                required=True
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def faculties_lock_user(ctx: SlashInteraction, faculty: discord.Role, user: discord.User):
        faculties = BotHelper.get_faculty_roles(ctx)
        faculty_roles = [i[2].id for i in faculties]
        if faculty in [i[2].id for i in faculties]:
            user = ctx.guild.get_member(user.id)
            user_roles = [i for i in user.roles if i.id in faculty_roles]
            faculty = ctx.guild.get_role(faculty)
            await ctx.reply(content=':thumbsup:', ephemeral=True, delete_after=1)
            await LoggingUtils.log_to_discord(ctx, 'User faculty got locked', LoggingUtils.LogLevels.INFO, user=user.mention, faculty=faculty.mention, initiator=ctx.author.mention)
            LoggingUtils.log_to_db('user_faculty_lock', user=ctx.author, target_user=user, other_data={'faculty_role_id': faculty.id, 'faculty_role': faculty.mention})

            if not (len(user_roles) == 1 and user_roles[0].id == faculty.id):
                try:
                    await user.remove_roles(*user_roles, reason="Removed by admin command")
                except Exception as e:
                    LoggingUtils.logger.exception(e)

                await user.add_roles(faculty, reason="Added by admin command")

            local_user = DB.get_user(user)
            local_user['faculty_id'] = faculty.id
            local_user['is_faculty_locked'] = True
            DB.set_user(local_user)
        else:
            await ctx.reply(content='That is not valid faculty role', ephemeral=True, delete_after=1)

    @faculties.sub_command(
        name='unlockuser',
        description='Set user\'s faculty and do not allow them to change it.',
        options=[
            Option(
                name='user',
                description='What user shall get locked',
                type=OptionType.USER,
                required=True
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def faculties_unlock_user(ctx: SlashInteraction, user: discord.User):
        local_user = DB.get_user(user)
        if local_user['is_faculty_locked']:
            await ctx.reply(content=':thumbsup:', ephemeral=True, delete_after=1)
            await LoggingUtils.log_to_discord(ctx, 'User faculty got un locked', LoggingUtils.LogLevels.INFO, user=user.mention, initiator=ctx.author.mention)
            LoggingUtils.log_to_db('user_faculty_unlock', user=ctx.author, target_user=user)

            local_user['is_faculty_locked'] = False
            DB.set_user(local_user)
        else:
            await ctx.reply(content='That user is not locked', ephemeral=True, delete_after=1)


async def on_faculty_role(ctx: MessageInteraction, selected: SelectOption):
    author_permission: Permissions = ctx.author.permissions_in(ctx.channel)
    faculty_roles = []
    user = DB.get_user(ctx.author)
    with DB.cursor() as cur:
        cur.execute("SELECT * FROM faculties order by title")
        for row in cur.fetchall():
            faculty_roles.append(row['role'])

    selected_role = int(selected.value)
    user_roles = [i for i in ctx.author.roles if i.id in faculty_roles]
    if len(user_roles) == 1 and not user['last_faculty_change']:
        user['faculty_id'] = user_roles[0].id
        user['last_faculty_change'] = datetime.now()-timedelta(20)
    if selected_role not in [i.id for i in user_roles]:
        if not user['is_faculty_locked']:
            change_interval = timedelta(days=DB.get_setting('faculty_change_interval_days', 30))
            if (user['last_faculty_change'] < datetime.now() - change_interval) or author_permission.manage_roles:
                try:
                    await ctx.author.remove_roles(*user_roles, reason="Updated from roles dropdown")
                except Exception as e:
                    LoggingUtils.logger.exception(e)

                try:
                    selected_role = ctx.guild.get_role(selected_role)
                    await ctx.author.add_roles(selected_role, reason="Updated from roles dropdown")
                    if user['faculty_id'] and user['faculty_id'] != selected_role.id:
                        await LoggingUtils.log_to_discord(
                            ctx,
                            'User changed their faculty',
                            LoggingUtils.LogLevels.WARN,
                            user=ctx.author.mention,
                            initial_faculty=ctx.guild.get_role(user['faculty_id']).mention,
                            new_faculty=selected_role.mention
                        )
                        LoggingUtils.log_to_db('faculties_user_reassigned', user=ctx.author, other_data={
                            'initial_facultyId': ctx.guild.get_role(user['faculty_id']).id,
                            'initial_faculty': ctx.guild.get_role(user['faculty_id']).mention,
                            'new_faculty_id': selected_role.id,
                            'new_faculty': selected_role.mention
                        })
                    user['faculty_id'] = selected_role.id
                    user['last_faculty_change'] = datetime.now()
                except Exception as e:
                    LoggingUtils.logger.exception(e)
                await ctx.reply('Tava fakultāte tika atjaunota', ephemeral=True, delete_after=2)
            else:
                await ctx.reply(f'Tu atkārtoti varēsi izvēlēties savu fakultāti {(datetime.now() + (change_interval-(datetime.now()-user["last_faculty_change"]))).strftime("%Y.%m.%d")}', ephemeral=True, delete_after=2)
        else:
            await ctx.reply('Tu nedrīksti mainīt savu fakultāti, ja tas tiešām ir nepieciešams, sazinies ar kādu no administratoriem', ephemeral=True, delete_after=2)
    else:
        await ctx.reply('Tu jau esi reģistrēts šajā fakultātē', ephemeral=True, delete_after=2)
        if selected_role != user['faculty_id']:
            user['faculty_id'] = selected_role
            user['last_faculty_change'] = datetime.now()
    DB.set_user(user)
    await update_faculty_stats(ctx)


async def update_faculty_stats(ctx):
    roles = BotHelper.get_faculty_roles(ctx)
    roles = sorted(roles, key=lambda x: len(x[2].members), reverse=True)
    embed = Embed(color=0xeaaa00)
    embed.title = 'Šobrīdējais fakultāšu pārstāvju skaits serverī'
    for title, icon, role in roles:
        if 'None' not in title:
            embed.add_field(
                name=f"{icon if icon else ''} {title}",
                value=f"{len(role.members)}",
                inline=True
            )
    with DB.cursor() as cur:
        cur.execute("SELECT * FROM messages")
        for row in cur.fetchall():
            if row['type'] == 'facultiesStats':
                try:
                    chat = ctx.guild.get_channel(row['channel'])
                    msg = chat.get_partial_message(row['message'])
                    if msg:
                        await msg.edit(embed=embed)
                except Exception as e:
                    pass