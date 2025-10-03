import os

import telebot
from groq import Groq

from chatbot import ChocolateJoe
from chatbot.prompter import Prompter
from chatbot.redis_db import RedisDB

if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN", "")

    bot = telebot.TeleBot(token)
    redis_db = RedisDB()
    prompter = Prompter()
    model = Groq()

    chocolate_joe = ChocolateJoe(bot, model, prompter, redis_db)
    chocolate_joe.notify()
    chocolate_joe.run_bot()
