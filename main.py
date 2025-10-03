import os

import telebot
from groq import Groq

from src.chatbot import ChocolateJoe
from src.chatbot.prompter import Prompter
from src.redis_db import RedisDB

if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN", "")

    bot = telebot.TeleBot(token)
    redis_db = RedisDB()
    prompter = Prompter()
    model = Groq()

    chocolate_joe = ChocolateJoe(bot, model, prompter, redis_db)
    # TODO this should be async + I think we'll need a cli intrface for this at some point
    chocolate_joe.clear_patchnote()
    chocolate_joe.notify()

    chocolate_joe.run_bot()
