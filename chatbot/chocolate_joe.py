from telebot import TeleBot
from telebot.types import Message

from .redis_db import RedisDB


class ChocolateJoe:
    def __init__(self, bot: TeleBot, llm, prompter, redis_db: RedisDB) -> None:
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

    def _display_patchnote(self, chat_id):
        self.bot.send_message(
            chat_id,
            "Sample text",
            parse_mode="Markdown",
        )

    def run_bot(self):
        self.bot.polling()

    def toggle_patchnotes(self, message: Message):
        current = self.redis_db.get(f"notify:{message.chat.id}")
        new = 0 if current == "1" else 1
        text = (
            "Аргх, матросы! Уведомления об обновлениях включены!"
            if new
            else "Apppp! Никаких больше патчноутов!"
        )

        self.redis_db.set(f"notify:{message.chat.id}", new)

        self.bot.send_message(
            message.chat.id,
            text,
            reply_to_message_id=message.id,
            parse_mode="Markdown",
        )

    def start_command(self, message: Message):
        # TODO move outside
        PRIVATE_HELP_MESSAGE = """
Ahoy! Я Шоколадный Джо, рассказывай, что тебе от меня нужно?
        """.strip()
        GROUP_HELP_MESSAGE = """
        Эй, я Шоколадный Джо! Я только вернулся с моря, а здесь чересчур шумно, так что захочешь поговорить — обращайся *по имени* или просто *@намекни*, чтобы я ответил. *Ответишь* на мои слова — я тоже в стороне не останусь.
С кем попало я языком чесать не буду. Захватишь 🍫 шоколад — тогда другое дело.
Понял? А теперь проваливай и дай мне допить свое какао!

Команды, черт их возьми. Чтобы мне, Шоколадному Джо...🔇:
- /start или /help - показать эту справку
- /togglepatchnotes - включить или выключить уведомления об обновлениях от самого Шоколадного Джо
- /patchnote - показать информацию о последнем обновлении
        """.strip()

        text = (
            PRIVATE_HELP_MESSAGE
            if message.chat.type == "private"
            else GROUP_HELP_MESSAGE
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

        prompt = self.prompter.get_context(message=message.text, username=username)
        response = self.llm.chat.completions.create(
            messages=prompt, model="openai/gpt-oss-120b"
        )
        response_text = response.choices[0].message.content
        if not response_text:
            response_text = "Респонса не будет, м."
        self.bot.send_message(
            message.chat.id,
            response_text,
            reply_to_message_id=message.id,
            parse_mode="Markdown",
        )
