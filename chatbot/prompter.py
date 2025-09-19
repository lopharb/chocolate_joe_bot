from .prompt import SYSTEM_MESSAGE, USER_MESSAGE

from groq.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionMessageParam,
)


class Prompter:
    def __init__(self, system_message=SYSTEM_MESSAGE, user_message=USER_MESSAGE):
        self.system_message = system_message
        self.user_message = user_message

    def get_context(
        self, message: str, username: str
    ) -> list[ChatCompletionMessageParam]:
        context = [
            ChatCompletionSystemMessageParam(
                {
                    "role": "system",
                    "content": self.system_message,
                }
            ),
            ChatCompletionUserMessageParam(
                {
                    "role": "user",
                    "content": self.user_message.format(
                        user_name=username,
                        user_message=message,
                    ),
                }
            ),
        ]

        return context
