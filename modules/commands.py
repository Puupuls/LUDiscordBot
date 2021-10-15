from discord import PartialEmoji
from discord.ext.commands import Context
from dislash import SelectOption, SelectMenu, MessageInteraction

from utils.bot_helper import prefix, set_prefix
from utils.database import DB


class Commands:
    @staticmethod
    async def help(ctx: Context):
        response = 'Available commands:\n'
        for c in sorted(ctx.bot.commands, key=lambda x: x.name):
            if not c.hidden:
                response += f"• {ctx.prefix}{c.name}{' ' + c.usage if c.usage else ''}\n"
                response += f"   {c.description}\n"
        await ctx.send(response)

    @staticmethod
    async def prefix(ctx: Context, new_prefix: str):
        if new_prefix:
            set_prefix(new_prefix)
            response = f'Prefix changed to "{new_prefix}"'
        else:
            response = f"Current prefix is \"{prefix()}\""
        await ctx.send(response)

    @staticmethod
    async def faculty_roles(ctx: Context):
        options = []
        with DB.cursor() as cur:
            cur.execute("SELECT * FROM faculties")
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
                        row['title'],
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
        msg = await ctx.send(
            content="Please select your LU faculty",
            components=[options]
        )
        await ctx.message.delete()

    @staticmethod
    async def on_faculty_role(ctx: MessageInteraction, selected: SelectOption):
        faculty_roles = []
        with DB.cursor() as cur:
            cur.execute("SELECT * FROM faculties")
            for row in cur.fetchall():
                faculty_roles.append(row['role'])

        selected_role = int(selected.value)
        user_roles = [i for i in ctx.author.roles if i.id in faculty_roles and i.id != selected_role]

        await ctx.author.remove_roles(*user_roles, reason="Updated from roles dropdown")

        try:
            selected_role = ctx.guild.get_role(selected_role)
            await ctx.author.add_roles(selected_role, reason="Updated from roles dropdown")
        except Exception as e:
            print(e)

        await ctx.reply('Your roles were updated', ephemeral=True)