import os

import telebot
from groq import Groq

from src.agent.prompts.prompter import Prompter
from src.chocolate_joe import ChocolateJoe
from src.database.redis_db import RedisClient
from src.utils.logger import setup_logger

if __name__ == "__main__":
    logger = setup_logger("chocolate-joe")

    token = os.environ.get("BOT_TOKEN", None)

    if token is None:
        logger.critical("BOT_TOKEN environment variable not set")
        exit(1)

    logger.info("Setting up underlying services.")
    try:
        bot = telebot.TeleBot(token)
        redis_db = RedisClient()
        prompter = Prompter()
        model = Groq()
        chocolate_joe = ChocolateJoe(bot, model, prompter, redis_db)
    except Exception as e:
        logger.critical(f"Failed to set up underlying services: {e}")
        exit(1)

    # TODO this should be async + I think we'll need a cli intrface for this at some point
    logger.info("Resetting patchnote.")
    chocolate_joe.clear_patchnote()

    logger.info("Notifying users.")
    chocolate_joe.notify()

    logger.info("Starting polling.")
    chocolate_joe.start_polling()
