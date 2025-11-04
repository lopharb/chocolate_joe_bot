from typing import List

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
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
    ) -> List[BaseMessage]:
        context = [
            SystemMessage(self.system_message),
            HumanMessage(
                self.user_message.format(
                    user_name=username,
                    user_message=message,
                ),
            ),
        ]

        return context

    def _prepare_readme(self, readme: str):
        chunks = readme.split("##")
        return "\n\n".join(chunks[:2])

    def get_patchnote_context(self, readme: str) -> List[BaseMessage]:
        patchnote = self._prepare_readme(readme)
        context = [
            SystemMessage(self.system_message),
            HumanMessage(
                self.patchnote_message.format(
                    patchnote=patchnote,
                )
            ),
        ]

        return context
