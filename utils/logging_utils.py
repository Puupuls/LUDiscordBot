import enum
import json
import logging
import os
import re
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import discord
from discord import Embed


class LoggingUtils:
    logger = logging.Logger(name='bot')

    class LogLevels(enum.Enum):
        INFO = 0x7777ff
        WARN = 0xffaa00
        DANGER = 0xff0000

    @staticmethod
    async def log_to_discord(ctx, message, level=LogLevels.INFO, **kwargs):
        from utils.database import DB
        log_channel_id = DB.get_setting('log_channel')
        if log_channel_id:
            try:
                channel = ctx.guild.get_channel(int(log_channel_id))

                embed = Embed(color=level.value)
                embed.title = LoggingUtils.LogLevels(level).name
                embed.description = message
                for k, v in kwargs.items():
                    embed.add_field(name=k, value=v, inline=False)
                await channel.send(embed=embed)
            except Exception as e:
                LoggingUtils.logger.error(e)

    @staticmethod
    def log_to_db(
            event_name: str,
            user: discord.User,
            message: discord.Message = None,
            channel: discord.TextChannel = None,
            target_user: discord.User = None,
            other_data: dict = None
    ):
        try:
            from utils.database import DB
            with DB.cursor() as cur:
                cur.execute("INSERT INTO log "
                            "(event_name, timestamp, user_id, user, message_id, channel_id, channel, target_user_id, target_user, other_data) VALUES "
                            "(?,          ?,         ?,       ?,    ?,          ?,          ?,       ?,              ?,           ?)",
                            (
                                event_name,
                                datetime.now(),
                                user.id,
                                user.mention,
                                message.id if message else None,
                                channel.id if message else None,
                                channel.mention if message else None,
                                target_user.id if message else None,
                                target_user.mention if message else None,
                                json.dumps(other_data)
                            ))
        except Exception as e:
            LoggingUtils.logger.error(e)

    @staticmethod
    def init(name):
        LoggingUtils.logger.setLevel(logging.DEBUG)
        os.makedirs('logs/', exist_ok=True)

        formatter = logging.Formatter(
            fmt='[%(asctime)s:%(msecs)d] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        handler = TimedRotatingFileHandler(f'logs/{name}.log', when="midnight", interval=1)
        handler.suffix = "%Y%m%d"
        handler.extMatch = re.compile(r"^\d{8}$")
        handler.setLevel(logging.DEBUG)
        handler.formatter = formatter
        LoggingUtils.logger.addHandler(handler)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.formatter = formatter
        LoggingUtils.logger.addHandler(handler)

