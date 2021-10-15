from enum import Enum

from discord import Guild
from utils.database import DB


class Roles(Enum):
    user = 1
    moderator = 2
    admin = 3


def prefix(guild: Guild):
    p = DB.get_setting(f'{guild.id}_PREFIX')
    if p is not None:
        return p
    return '!'


def set_prefix(guild: Guild, new_prefix: str):
    DB.set_setting(f'{guild.id}_PREFIX', new_prefix)


def get_server_roles(guild: Guild) -> dict:
    roles = {}
    with DB.cursor() as cur:
        cur.execute("SELECT discord_role_id, permission_level FROM roles where guild_id = ?", (guild.id,))
        for row in cur.fetchall():
            dr, pl = row['discord_role_id'], row['permission_level']
            for r in Roles:
                if pl == r.value:
                    pl = r
            for i in guild.roles + guild.members:
                if i.id == dr:
                    dr = i
            if type(dr) == int:  # Remove roles that do not exist anymore
                cur.execute("DELETE FROM roles WHERE guild_id=? and permission_level=? and discord_role_id=?", (
                    guild.id,
                    pl,
                    dr,
                ))
            if pl in roles:
                roles[pl].append(dr)
            else:
                roles[pl] = [dr]
        if Roles.user not in roles:
            roles[Roles.user] = [guild.default_role]
    return roles


def store_server_role(guild, level, discord_role):
    with DB.cursor() as cur:
        cur.execute("INSERT INTO roles (guild_id, discord_role_id, permission_level) values (?, ?, ?)",
                    (
                        guild.id,
                        discord_role.id,
                        level.value
                    ))


async def return_command_error(message, error, command):
    await message.channel.send(f"{error}, see `{prefix(message.guild)}help {command}` for more info")
