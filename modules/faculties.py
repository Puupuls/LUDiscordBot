from datetime import datetime, timedelta
from discord import Permissions, PartialEmoji, Embed
from discord.ext.commands import Bot
from dislash import SlashInteraction, MessageInteraction, SelectOption, SelectMenu, has_permissions, InteractionClient
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
        await update_faculty_stats(ctx)


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
    if len(user_roles) == 1:
        user['faculty_id'] = user_roles[0].id
        user['last_faculty_change'] = datetime.now()-timedelta(20)
    if user['faculty_id'] not in [i.id for i in user_roles]:
        if not user['is_faculty_locked']:
            change_interval = timedelta(days=DB.get_setting('faculty_change_interval_days', 30))
            if user['last_faculty_change'] < datetime.now() - change_interval or author_permission.manage_roles:
                try:
                    await ctx.author.remove_roles(*user_roles, reason="Updated from roles dropdown")
                except Exception as e:
                    print(e)

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
                    user['faculty_id'] = selected_role.id
                    user['last_faculty_change'] = datetime.now()
                except Exception as e:
                    print(e)
                await ctx.reply('Tava fakultāte tika atjaunota', ephemeral=True, delete_after=2)
            else:
                await ctx.reply(f'Tu atkārtoti varēsi izvēlēties savu fakultāti {(datetime.now() + (change_interval-(datetime.now()-user["last_faculty_change"]))).strftime("%Y.%m.%d")}', ephemeral=True, delete_after=2)
        else:
            await ctx.reply('Tu nedrīksti mainīt savu fakultāti, ja tas tiešām ir nepieciešams, sazinies ar administratoriem', ephemeral=True, delete_after=2)
    else:
        await ctx.reply('Tu jau esi reģistrēts šajā fakultātē', ephemeral=True, delete_after=2)
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