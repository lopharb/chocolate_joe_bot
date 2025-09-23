import os

import telebot
from groq import Groq

from chatbot import ChocolateJoe
from chatbot.prompter import Prompter


if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN", "")

    bot = telebot.TeleBot(token)
    prompter = Prompter()
    model = Groq()

    chocolate_joe = ChocolateJoe(bot, model, prompter)
    chocolate_joe.run_bot()
