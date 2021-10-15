import re
from discord import Guild, User, Message
from discord.ext.commands import Bot

from utils.database import DB


def prefix(bot: Bot = None, message: Message = None):
    p = DB.get_setting(f'PREFIX', '!')
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


def mention_to_id(mention):
    try:
        i = re.match('/<[#@]?[!?]?(\d+)>/', mention)
        return i.groups()[0]
    except:
        return None
