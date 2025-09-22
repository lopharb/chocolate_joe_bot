import os

import telebot
from telebot.types import Message
from groq import Groq

from chatbot.prompter import Prompter

token = os.environ.get("BOT_TOKEN", "")

bot = telebot.TeleBot(token)
prompter = Prompter()
model = Groq()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id, "Я Шоколадный Джо, и теперь в этом чате господствую я!"
    )


@bot.message_handler()
def help(message: Message):
    if message.text is None:
        return
    if message.text.lower().find("шоколадный джо") == -1:
        return
    if message.from_user is None:
        return

    username = message.from_user.first_name
    if message.from_user.last_name:
        username += f" {message.from_user.last_name}"
    prompt = prompter.get_context(message=message.text, username=username)
    response = model.chat.completions.create(
        messages=prompt, model="openai/gpt-oss-120b"
    )
    response_text = response.choices[0].message.content
    if not response_text:
        response_text = "razrab eblan"
    bot.send_message(
        message.chat.id,
        response_text,
        reply_to_message_id=message.id,
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    bot.polling()
