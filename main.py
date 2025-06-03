import os

import telebot
from telebot.types import Message

from chatbot.ollama_client import OllamaModel
from chatbot.prompter import Prompter

token = os.environ.get("BOT_TOKEN", "")

bot = telebot.TeleBot(token)
prompter = Prompter()
model = OllamaModel('llama-3.1')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Я Шоколадный Джо, и теперь в этом чате господствую я!")

@bot.message_handler()
def help(message : Message):
    if message.text is None:
        return
    if message.text.lower().find('шоколадный джо') == -1:
        return
    if message.from_user is None:
        return

    username = f'{message.from_user.first_name} {message.from_user.last_name}'
    prompt = prompter.get_context(message=message.text, username=username)
    response = model.get_response(prompt)
    bot.send_message(message.chat.id, response, reply_to_message_id=message.id)

if __name__ == "__main__":
    bot.polling()
