from telebot.types import Message
from telebot import TeleBot


class ChocolateJoe:
    def __init__(self, bot: TeleBot, llm, prompter) -> None:
        self.bot = bot
        self.llm = llm
        self.prompter = prompter
        self.mentions = [
            "шоколадный джо",
            "chocolate joe",
            f"@{self.bot.user.username}",
        ]

        # TODO questionable pattern, may require changes
        # resister the handlers
        self.bot.message_handler(commands=["start"])(self.start_command)
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

    def run_bot(self):
        self.bot.polling()

    def start_command(self, message: Message):
        self.bot.send_message(
            message.chat.id, "Я Шоколадный Джо, и теперь в этом чате господствую я!"
        )

    def handle_message(self, message: Message) -> str | None:
        # hacky but all the fields are optional
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
