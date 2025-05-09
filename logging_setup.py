import logging
from logging.handlers import RotatingFileHandler


# ====== Logging Setup ======
logger = logging.getLogger("telegram-bot")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=3)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)