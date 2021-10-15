from discord import Client, Message
from utils.bot_helper import Roles, return_command_error, store_server_role
from utils.bot_helper import prefix, set_prefix, get_server_roles
from utils.database import DB

COMMANDS = {
    'help': {
        "usage": "<command>",
        "description": "See all available commands or more information about a specific one.",
        "required_role": Roles.user,
        "aliases": ['h']
    },
    'prefix': {
        "usage": "[new-prefix]",
        "description": "Change bot command prefix, you can always use bot by mentioning it at the begining of the message",
        "required_role": Roles.admin,
        "aliases": []
    },
    'role': {
        "usage": f"<add|remove|list> [{'|'.join([e.name for e in Roles])}] [user|role]",
        "description": "Change or list role or user permissions",
        "required_role": Roles.admin,
        "aliases": []
    },
}


class CommandHandler:
    @staticmethod
    async def handle(client: Client, message: Message,):
        msg = message.content.lstrip(prefix(message.guild))
        msg = msg.lstrip(f"<@!{client.user.id}>")
        msg = msg.strip()
        msg = msg.split()
        command, args = msg[0], msg[1:]

        # Handle aliases
        for cmd in COMMANDS:
            if command == cmd or command in COMMANDS[cmd]['aliases']:
                command = cmd

        # Check if it is an existing command
        if command in COMMANDS:
            roles = get_server_roles(message.guild)

            # Verify that user has permissions to do that
            if (
                    COMMANDS[command]['required_role'] in roles and
                    (
                            any([True for i in roles[COMMANDS[command]['required_role']] if i in message.author.roles]) or
                            message.author in roles[COMMANDS[command]['required_role']]
                    )
            ) or message.author.guild_permissions.administrator:
                if command == 'help':
                    response = ''
                    if len(args) == 0:
                        response += f"Prefix `{prefix(message.guild)}` and `{client.user.mention}` is interchangeable.\n"
                        for cmd, h in COMMANDS.items():
                            response += f"{prefix(message.guild)}{cmd} {h['usage']}\n"
                    elif args[0] in COMMANDS:
                        response += f"{prefix(message.guild)}{args[0]} {COMMANDS[args[0]]['usage']}\n"
                        response += f"{COMMANDS[args[0]]['description']}"
                    else:
                        response += f"Unknown command, can't help with that, try `{prefix(message.guild)}help` to see what you can do"

                    await message.channel.send(response)

                if command == 'prefix':
                    if len(args) == 0:
                        await message.channel.send(f"Current prefix is {prefix(message.guild)}")
                    elif len(args) > 0:
                        set_prefix(message.guild, args[0])
                        await message.channel.send(f"Prefix changed to {prefix(message.guild)}")
                    else:
                        await return_command_error(message, 'Too many arguments provided', 'prefix')

                if command == 'role':
                    if len(args) < 1:
                        await return_command_error(message, 'Not enough arguments provided', 'role')
                    elif len(args) == 1 and args[0] == 'list':
                        if len(args) == 1:
                            response = 'Current roles: \n'
                            for m in Roles:
                                if m in roles:
                                    response += f"{m.name}: [{', '.join([i.name.replace('@', '') for i in roles[m]])}]\n"
                                else:
                                    response += f"{m.name}: []\n"
                            await message.channel.send(response)
                    elif len(args) == 3 and args[0] in ['add', 'remove']:
                        if args[0] == 'add':
                            if args[1] in [i.name for i in Roles]:
                                target = []

                                if not target:
                                    for r in message.guild.roles:
                                        if args[2].lower() in r.name.lower() or args[2][3:-1] == str(r.id):
                                            target.append(r)
                                if not target:
                                    for m in message.guild.members:
                                        if args[2].lower() in m.name.lower() or args[2].lower() in (m.nick.lower() if m.nick else '') or args[2][3:-1] == str(m.id):
                                            target.append(m)
                                if not target:
                                    await message.channel.send('Could not find target user or role')
                                elif len(target) > 1:
                                    await message.channel.send(f'Found multiple possible targets: [{[",".join([str(i) for i in target])]}]')
                                else:
                                    if target[0] not in roles.get(args[1], []):
                                        store_server_role(message.guild, Roles._member_map_[args[1]], target[0])
                                        await message.channel.send(f"Added {args[2]} to {args[1]} role")

                    else:
                        await return_command_error(message, 'Wrong amount of arguments provided', 'role')

        if command == 'reset_db':
            DB.clean_db()
            await message.channel.send('Success')