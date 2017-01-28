import logging
import threading

from yausyb.core import BotCore
from yausyb.logger import logger

logger.setLevel(logging.DEBUG)
finish = threading.Event()
bot = BotCore()

while not finish.wait(3600):
    pass
