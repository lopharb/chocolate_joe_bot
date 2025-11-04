from telebot import TeleBot
from telebot.types import Message

from .agent.prompts import command_messages as cm
from .agent.prompts.prompter import Prompter
from .database.redis_db import RedisClient


class ChocolateJoe:
    def __init__(
        self, bot: TeleBot, llm, prompter: Prompter, redis_db: RedisClient
    ) -> None:
        self.bot = bot
        self.llm = llm
        self.prompter = prompter
        self.redis_db = redis_db
        self.mentions = [
            "🍫",
            "джо",
            "шоколадный джо",
            "chocolate joe",
            f"@{self.bot.user.username}",
        ]

        command_handlers = {
            "start": {"handler": self.start_command, "aliases": ["help"]},
            "togglepatchnotes": {"handler": self.toggle_patchnotes},
            "patchnote": {"handler": self.pathcnote},
        }
        for command, handler in command_handlers.items():
            command_list = [command] + handler.get("aliases", [])
            self.bot.message_handler(commands=command_list)(handler["handler"])
        self.bot.message_handler()(self.handle_message)

    def _needs_response(self, message: Message) -> bool:
        if message.text is None:
            return False

        if message.chat.type == "private":
            return True

        for mention in self.mentions:
            if mention in message.text.lower():
                return True

        if message.reply_to_message is not None:
            if message.reply_to_message.from_user.id == self.bot.user.id:
                return True

        return False

    def clear_patchnote(self):
        self.redis_db.delete("patchnote")

    def _get_patchnote(self) -> str:
        with open("README.md", "r") as file:
            readme = file.read()

        existing = self.redis_db.get("patchnote")
        if existing:
            return existing

        context = self.prompter.get_patchnote_context(readme)
        response = self.llm.chat.completions.create(
            messages=context, model="openai/gpt-oss-120b"
        )
        response_text = response.choices[0].message.content
        self.redis_db.set("patchnote", response_text)

        return response_text

    def _display_patchnote(self, chat_id):
        text = self._get_patchnote()
        self.bot.send_message(
            chat_id,
            text,
            parse_mode="Markdown",
        )

    def start_polling(self):
        self.bot.polling()

    def toggle_patchnotes(self, message: Message):
        current = self.redis_db.get(f"notify:{message.chat.id}")
        new = 0 if current == "1" else 1
        text = cm.NOTIFS_ON if new else cm.NOTIFS_OFF

        self.redis_db.set(f"notify:{message.chat.id}", new)

        self.bot.send_message(
            message.chat.id,
            text,
            reply_to_message_id=message.id,
            parse_mode="Markdown",
        )

    def start_command(self, message: Message):
        text = (
            cm.PRIVATE_HELP_MESSAGE
            if message.chat.type == "private"
            else cm.GROUP_HELP_MESSAGE
        )
        self.bot.send_message(message.chat.id, text, parse_mode="Markdown")

        previous_notif_setting = self.redis_db.get(f"notify:{message.chat.id}")
        if previous_notif_setting is None:
            self.redis_db.set(f"notify:{message.chat.id}", "1")

    def pathcnote(self, message: Message):
        chat_id = message.chat.id
        self._display_patchnote(chat_id)

    def notify(self):
        for key in self.redis_db.get_keys_by_root("notify"):
            chat_id = key.split(":")[1]
            config = self.redis_db.get(key)
            if config == "1":
                self._display_patchnote(chat_id)

    def handle_message(self, message: Message) -> str | None:
        # TODO figure out a better way
        try:
            if not self._needs_response(message):
                return

        except Exception:
            return

        assert message.from_user is not None
        assert message.text is not None

        username = message.from_user.first_name
        if message.from_user.last_name:
            username += f" {message.from_user.last_name}"

        prompt = self.prompter.get_message_context(
            message=message.text, username=username
        )
        response = self.llm.chat.completions.create(
            messages=prompt, model="openai/gpt-oss-120b"
        )
        response_text = response.choices[0].message.content
        if not response_text:
            response_text = "Респонса не будет, м."
        self.bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            reply_to_message_id=message.id,
            parse_mode="Markdown",
        )
