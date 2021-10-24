from discord.ext.commands import Bot
from dislash import Option, OptionType, SlashInteraction, has_permissions, InteractionClient
from utils.database import DB
from utils.logging_utils import LoggingUtils


def register_commands_rule(slash: InteractionClient, client: Bot):
    @slash.command(
        name='rule'
    )
    async def rule(ctx):
        pass

    @rule.sub_command(
        name='create_message',
        description='Create rules message in current chat',
    )
    @has_permissions(administrator=True)
    async def rule_create_msg(ctx: SlashInteraction):
        await ctx.reply('Creating rules message', ephemeral=True, delete_after=2)
        msg = await ctx.channel.send('**=== NOTEIKUMI ===**')
        with DB.cursor() as cur:
            cur.execute("INSERT INTO messages (channel, message, type) VALUES (?, ?, ?)", (msg.channel.id, msg.id, 'rules'))

        LoggingUtils.log_to_db('rules_message_sent', user=ctx.author, channel=ctx.channel)
        await update_rules_message(ctx)

    @rule.sub_command(
        name='add',
        description='Add new rule',
        options=[
            Option(
                name='message',
                description='The message to send',
                type=OptionType.STRING,
                required=True
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def rule_add(ctx: SlashInteraction, message: str):
        await ctx.reply('Updating rules', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:
            cur.execute("SELECT max(id) as mid FROM rules")
            mid = cur.fetchone()['mid']
            if not mid:
                mid = 0
            cur.execute("INSERT INTO rules VALUES "
                        "(?, ?)", (mid + 1, message,))
            LoggingUtils.log_to_db('rules_added', user=ctx.author, other_data={'message': message})
        await update_rules_message(ctx)

    @rule.sub_command(
        name='update',
        description='Change rule text',
        options=[
            Option(
                name='id',
                description='Rule order id',
                type=OptionType.INTEGER,
                required=True
            ),
            Option(
                name='message',
                description='The message to send',
                type=OptionType.STRING,
                required=True
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def rule_remove(ctx: SlashInteraction, id: int, message: str):
        await ctx.reply('Updating rule', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:
            cur.execute('UPDATE rules SET rule = ? WHERE id = ?', (message, id,))
        LoggingUtils.log_to_db('rules_updated', user=ctx.author, other_data={'message': message, 'rule_id': id})

        await update_rules_message(ctx)

    @rule.sub_command(
        name='remove',
        description='Remove rule',
        options=[
            Option(
                name='id',
                description='Rule order id',
                type=OptionType.INTEGER,
                required=True
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def rule_remove(ctx: SlashInteraction, id: int):
        await ctx.reply('Updating rules', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:
            cur.execute('DELETE FROM rules WHERE id=?', (id,))
            cur.execute('UPDATE rules SET id = id-1 WHERE id > ?', (id,))
        LoggingUtils.log_to_db('rules_removed', user=ctx.author, other_data={'rule_id': id})

        await update_rules_message(ctx)

    @rule.sub_command(
        name='reposition',
        description='Change rules position in list',
        options=[
            Option(
                name='id',
                description='Rule order id',
                type=OptionType.INTEGER,
                required=True
            ),
            Option(
                name='new_pos',
                description='New position of role in list',
                type=OptionType.INTEGER,
                required=True
            ),
        ]
    )
    @has_permissions(administrator=True)
    async def rule_move(ctx: SlashInteraction, id: int, new_pos: int):
        await ctx.reply('Updating rules:', ephemeral=True, delete_after=2)
        with DB.cursor() as cur:
            cur.execute('UPDATE rules SET id = id+1 WHERE id >= ?', (new_pos,))
            cur.execute('UPDATE rules SET id = ? WHERE id = ?', (new_pos, id + 1))
        LoggingUtils.log_to_db('rules_reordered', user=ctx.author, other_data={'rule_id': id, 'new_id': new_pos})

        await update_rules_message(ctx)


async def update_rules_message(ctx):
    message = "**=== NOTEIKUMI ===**\n"
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