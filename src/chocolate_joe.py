from logging import getLogger

from telebot import TeleBot
from telebot.types import Message

from .agent.lc_agent import LCAgent
from .agent.prompts import command_messages as cm
from .database.redis_db import RedisClient


class ChocolateJoe:
    def __init__(
        self,
        bot: TeleBot,
        agent: LCAgent,
        redis_db: RedisClient,
    ) -> None:
        self.bot = bot
        self.agent = agent
        self.redis_db = redis_db
        self.mentions = [
            "🍫",
            "джо",
            "шоколадный джо",
            "chocolate joe",
            f"@{self.bot.user.username}",
        ]
        self._logger = getLogger("chocolate-joe")

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
            if message.reply_to_message.from_user is None:
                self._logger.warning("User not set for the message.")
                return False
            if message.reply_to_message.from_user.id == self.bot.user.id:
                return True

        return False

    def clear_patchnote(self):
        self._logger.info("Clearing patchnote.")
        self.redis_db.delete("patchnote")

    def _get_patchnote(self) -> str:
        self._logger.info("Checking for existing patchnote.")
        existing = self.redis_db.get("patchnote")
        if existing:
            self._logger.info("Patchnote found. Reusing.")
            return existing

        generated_patchnote = self.agent.generate_patchnote()
        self.redis_db.set("patchnote", generated_patchnote.content)
        patchnote_text = str(generated_patchnote.content)

        return patchnote_text

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

        self._logger.info(f"Patchnotes set to {new} for chat {message.chat.id}.")

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
        for key in self.redis_db.find("notify"):
            chat_id = key.split(":")[1]
            config = self.redis_db.get(key)
            if config == "1":
                self._display_patchnote(chat_id)

    def handle_message(self, message: Message) -> str | None:
        needs_response = self._needs_response(message)
        response = self.agent.handle_message(message, needs_response)
        if response is None:
            return

        response_text = str(response.content)

        try:
            self.bot.send_message(
                chat_id=message.chat.id,
                text=response_text,
                reply_to_message_id=message.id,
                parse_mode="Markdown",
            )
        except Exception as e:
            self._logger.error(
                f"Encountered {e.__class__.__name__} while sending message: {e}."
            )
