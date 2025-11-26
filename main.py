import os

import telebot
from langchain_groq.chat_models import ChatGroq
from redis import Redis

from src.agent.lc_agent import LCAgent
from src.agent.prompts.prompter import Prompter
from src.agent.redis_history import RedisHistoryManager
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
        redis = Redis(host="redis")
        redis_hm = RedisHistoryManager(redis)
        redis_db = RedisClient()
        prompter = Prompter()
        model = ChatGroq(model="openai/gpt-oss-120b")
        agent = LCAgent(model, prompter, redis_hm)
        chocolate_joe = ChocolateJoe(bot, agent, redis_db)
    except Exception as e:
        logger.critical(f"Failed to set up underlying services: {e}")
        exit(1)

    chocolate_joe.clear_patchnote()
    chocolate_joe.notify()

    logger.info("Starting polling.")
    chocolate_joe.start_polling()
