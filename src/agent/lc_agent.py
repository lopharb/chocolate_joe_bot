import logging
from typing import List

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.human import HumanMessage
from langchain_groq import ChatGroq
from telebot.types import Message

from .prompts import Prompter
from .redis_history import RedisHistoryManager


class LCAgent:
    def __init__(
        self,
        llm: ChatGroq,
        prompter: Prompter,
        redis_history_manager: RedisHistoryManager,
        history_ttl: int = 5 * 60,
    ):
        self.llm = llm
        self.prompter = prompter
        self.redis_hm = redis_history_manager
        self.history_ttl = history_ttl
        self._logger = logging.getLogger("chocolate-joe")

    def get_chat_context(
        self, chat_id: int, message_text: str
    ) -> List[BaseMessage]:
        history = self.redis_hm.get_chat_history(chat_id)
        # TODO: should remove the prompter atp
        message_context = self.prompter.get_message_context(message_text)
        full_context = (
            [message_context[0]] + history + [message_context[1]]
        )  # system + history + user

        return full_context

    def get_response(self, message: Message) -> AIMessage:
        text = f"**{message.from_user.full_name}**: \n{message.text}"
        self.redis_hm.store_message(
            HumanMessage(content=text),
            message.chat.id,
            5 * 60,
        )

        context = self.get_chat_context(message.chat.id, text)
        response = self.llm.invoke(context)
        self.redis_hm.store_message(response, message.chat.id, 5 * 60)

        return response
