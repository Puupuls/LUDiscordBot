import re
from discord import Guild, User, Message, PartialEmoji
from discord.ext.commands import Bot

from utils.database import DB


def prefix(bot: Bot = None, message: Message = None):
    try:
        p = DB.get_setting(f'PREFIX', '!')
    except:
        p = '!'
        DB.clean_db()
    if p is not None:
        if bot:
            return [p, f"<@!{bot.user.id}>"]
        else:
            return p
    return '!'


def set_prefix(new_prefix: str):
    DB.set_setting(f'PREFIX', new_prefix)


def has_permissions(user: User):
    return True


def get_faculty_roles(ctx):
    with DB.cursor() as cur:
        roles = []
        cur.execute("SELECT * FROM faculties")
        for row in cur.fetchall():
            r = ctx.guild.get_role(row['role'])
            emoji = None
            try:
                for e in ctx.guild.emojis:
                    if e.name.lower() == row['icon'].lower():
                        emoji = e
            except:
                pass
            if r:
                roles.append([
                    row['title'].strip(),
                    PartialEmoji(
                        name=emoji.name if emoji else None,
                        id=emoji.id if emoji else None
                    ) if emoji else None,
                    r
                ])
    return roles


def mention_to_id(mention):
    try:
        i = re.match('/<[#@]?[!?]?(\d+)>/', mention)
        return i.groups()[0]
    except:
        return None
