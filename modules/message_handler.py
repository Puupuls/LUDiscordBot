from discord import Message, Client
from modules.command_executer import CommandHandler
from utils.bot_helper import prefix
from utils.logging_utils import LoggingUtils


class MessageHandler:
    @staticmethod
    async def handle(message: Message, client: Client):
        if message.content.startswith(prefix(message.guild)) or client.user in message.mentions and message.content.startswith(f"<@!{client.user.id}>"):
            LoggingUtils.logger.info(f"Processing command: "
                         f"[{message.author.display_name}] ({message.author.name}#{message.author.discriminator}) "
                         f"<{message.guild.name} / {message.guild.id}>: "
                         f"{message.content}")
            await CommandHandler.handle(client, message)
