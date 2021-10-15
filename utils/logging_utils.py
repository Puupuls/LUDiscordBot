import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler


class LoggingUtils:
    logger = logging.Logger(name='bot')

    @staticmethod
    def init(name):
        LoggingUtils.logger.setLevel(logging.DEBUG)
        os.makedirs('logs/', exist_ok=True)

        handler = TimedRotatingFileHandler(f'logs/{name}.log', when="midnight", interval=1)
        handler.suffix = "%Y%m%d"
        handler.extMatch = re.compile(r"^\d{8}$")
        handler.setLevel(logging.DEBUG)
        handler.formatter = logging.Formatter(
            fmt='[%(asctime)s:%(msecs)d] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        LoggingUtils.logger.addHandler(handler)
