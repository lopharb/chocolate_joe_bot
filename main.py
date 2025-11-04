import os

import telebot
from groq import Groq

from src.agent.prompts.prompter import Prompter
from src.chocolate_joe import ChocolateJoe
from src.database.redis_db import RedisClient

if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN", "")

    bot = telebot.TeleBot(token)
    redis_db = RedisClient()
    prompter = Prompter()
    model = Groq()

    chocolate_joe = ChocolateJoe(bot, model, prompter, redis_db)
    # TODO this should be async + I think we'll need a cli intrface for this at some point
    chocolate_joe.clear_patchnote()
    chocolate_joe.notify()

    chocolate_joe.start_polling()
