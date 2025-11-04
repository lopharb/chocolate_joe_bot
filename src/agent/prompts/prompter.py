from groq.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from .joe import SYSTEM_MESSAGE, USER_MESSAGE
from .tasks import PATCHNOTE_BUILD_MESSAGE


class Prompter:
    def __init__(
        self,
        system_message=SYSTEM_MESSAGE,
        user_message=USER_MESSAGE,
        patchnote_message=PATCHNOTE_BUILD_MESSAGE,
    ):
        self.system_message = system_message
        self.user_message = user_message
        self.patchnote_message = patchnote_message

    def get_message_context(
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

    def _prepare_readme(self, readme: str):
        chunks = readme.split("##")
        return "\n\n".join(chunks[:2])

    # xd
    # TODO prompter needs to go 4sure
    def get_patchnote_context(self, readme: str):
        patchnote = self._prepare_readme(readme)
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
                    "content": self.patchnote_message.format(
                        patchnote=patchnote,
                    ),
                }
            ),
        ]

        return context
