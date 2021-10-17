import discord
from discord import PartialEmoji, Embed
from dislash import SelectOption, SelectMenu, MessageInteraction, SlashInteraction

from utils.bot_helper import get_faculty_roles
from utils.database import DB


class Commands:
    @staticmethod
    async def faculty_roles(ctx: SlashInteraction):
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
            placeholder='Please select your faculty'
        )
        msg = await ctx.channel.send(
            content="Please select your LU faculty (Choose your current/latest one)",
            components=[options]
        )
        with DB.cursor() as cur:
            cur.execute("INSERT INTO messages (channel, message, type) VALUES (?, ?, ?)", (msg.channel.id, msg.id, 'facultiesSelect'))

    @staticmethod
    async def on_faculty_role(ctx: MessageInteraction, selected: SelectOption):
        faculty_roles = []
        with DB.cursor() as cur:
            cur.execute("SELECT * FROM faculties order by title")
            for row in cur.fetchall():
                faculty_roles.append(row['role'])

        selected_role = int(selected.value)
        user_roles = [i for i in ctx.author.roles if i.id in faculty_roles and i.id != selected_role]
        try:
            await ctx.author.remove_roles(*user_roles, reason="Updated from roles dropdown")
        except Exception as e:
            print(e)

        try:
            selected_role = ctx.guild.get_role(selected_role)
            await ctx.author.add_roles(selected_role, reason="Updated from roles dropdown")
        except Exception as e:
            print(e)

        await ctx.reply('Your roles were updated', ephemeral=True, delete_after=2)
        await Commands.update_faculty_stats(ctx)

    @staticmethod
    async def faculty_stats(ctx: SlashInteraction):
        embed = Embed(color=0xeaaa00)
        embed.title = 'Current count of faculty members in this server'
        msg = await ctx.channel.send(embed=embed)

        with DB.cursor() as cur:
            cur.execute("INSERT INTO messages (channel, message, type) VALUES (?, ?, ?)", (msg.channel.id, msg.id, 'facultiesStats'))

        await Commands.update_faculty_stats(ctx)

    @staticmethod
    async def update_faculty_stats(ctx):
        roles = get_faculty_roles(ctx)
        roles = sorted(roles, key=lambda x: len(x[2].members), reverse=True)
        embed = Embed(color=0xeaaa00)
        embed.title = 'Current count of faculty members in this server'
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

    @staticmethod
    async def send_post(ctx: SlashInteraction, channel: discord.TextChannel, message: str):
        if isinstance(channel, discord.TextChannel):
            await channel.send(message.encode("utf-8").decode("unicode_escape"))
            await ctx.send(':thumbsup:', ephemeral=True, delete_after=1)
        else:
            await ctx.reply('You must provide text channel', ephemeral=True, delete_after=2)

    @staticmethod
    async def edit_post(ctx: SlashInteraction, channel: discord.TextChannel, message_id: int, message: str):
        if isinstance(channel, discord.TextChannel):
            try:
                msg = channel.get_partial_message(message_id)
                if msg:
                    try:
                        await msg.edit(content=message.encode("utf-8").decode("unicode_escape"))
                        await ctx.reply(':thumbsup:', ephemeral=True, delete_after=1)
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

    @staticmethod
    async def rules_message(ctx: SlashInteraction):
        await ctx.reply('Creating rules message:', ephemeral=True, delete_after=2)
        msg = await ctx.channel.send('**=== RULES ===**')
        with DB.cursor() as cur:
            cur.execute("INSERT INTO messages (channel, message, type) VALUES (?, ?, ?)", (msg.channel.id, msg.id, 'rules'))

        await Commands.update_rules_message(ctx)

    @staticmethod
    async def update_rules_message(ctx: SlashInteraction):
        message = "**=== RULES ===**\n"
        with DB.cursor() as cur:
            cur.execute("SELECT * FROM rules ORDER BY id")

            for row in cur.fetchall():
                message += f"**{row['id']}**: {row['rule']}\n"

            cur.execute("SELECT * FROM messages")
            for row in cur.fetchall():
                if row['type'] == 'rules':
                    try:
                        chat = ctx.guild.get_channel(row['channel'])
                        msg = chat.get_partial_message(row['message'])
                        if msg:
                            await msg.edit(content=message)
                    except Exception as e:
                        pass

    @staticmethod
    async def rules_add(ctx: SlashInteraction, msg: str):
        await ctx.reply('Updating rules:', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:
            cur.execute("SELECT max(id) as mid FROM rules")
            mid = cur.fetchone()['mid']
            if not mid:
                mid = 0
            cur.execute("INSERT INTO rules VALUES "
                        "(?, ?)", (mid+1, msg,))

        await Commands.update_rules_message(ctx)

    @staticmethod
    async def rules_remove(ctx: SlashInteraction, rid: int):
        await ctx.reply('Updating rules:', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:
            cur.execute('DELETE FROM rules WHERE id=?', (rid,))
            cur.execute('UPDATE rules SET id = id-1 WHERE id > ?', (rid,))

        await Commands.update_rules_message(ctx)

    @staticmethod
    async def rules_reorder(ctx: SlashInteraction, rid: int, new_id: int):
        await ctx.reply('Updating rules:', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:

            cur.execute('UPDATE rules SET id = id+1 WHERE id >= ?', (new_id,))
            cur.execute('UPDATE rules SET id = ? WHERE id = ?', (new_id, rid + 1))

        await Commands.update_rules_message(ctx)
