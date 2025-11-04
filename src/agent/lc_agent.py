import json
import logging
from typing import List
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from telebot.types import Message

from ..database.redis_db import RedisClient
from .prompts import Prompter


class LCAgent:
    def __init__(
        self,
        llm: ChatGroq,
        prompter: Prompter,
        redis_db: RedisClient,
        history_ttl: int = 5 * 60,
    ):
        self.llm = llm
        self.prompter = prompter
        self.redis_db = redis_db
        self.history_ttl = history_ttl
        self._logger = logging.getLogger("chocolate-joe")

    def _store_history(self, chat_id: int, message: BaseMessage):
        message_id = str(uuid4().hex)
        key = f"history:{chat_id}:{message_id}"
        value = {
            "content": message.content,
            "role": "ai" if isinstance(message, HumanMessage) else "user",
        }
        self._logger.info(
            f"Storing message with ID {message_id} for chat {chat_id} under key {key}"
        )
        self.redis_db.set(key, json.dumps(value), ttl=self.history_ttl)

    def _get_history(self, chat_id: int) -> list[BaseMessage]:
        self._logger.info(f"Retrieving history for chat {chat_id}.")
        self._logger.info(f"Using key 'history:{chat_id}:'.")

        history = []
        for key in self.redis_db.find(f"history:{chat_id}:*"):
            self._logger.info(f"Retrieving message by key {key}.")
            message = self.redis_db.get(key)

            if message is None:
                self._logger.warning("Empty message in Redis.")
                continue

            message = json.loads(message)
            role = message["role"]
            self._logger.info(f"Retrieved message with role {role}.")
            if role == "user":
                history.append(HumanMessage(content=message["content"]))
            elif role == "ai":
                history.append(AIMessage(content=message["content"]))
        self._logger.info(
            f"Retrieved {len(history)} messages for chat {chat_id}."
        )

        return history

    def get_chat_context(
        self, chat_id: int, new_message: Message
    ) -> List[BaseMessage]:
        history = self._get_history(chat_id)
        # TODO handle Nonetype
        message_context = self.prompter.get_message_context(
            new_message.text, new_message.from_user.full_name
        )
        # TODO: should remove the prompter atp
        full_context = (
            [message_context[0]] + history + [message_context[1]]
        )  # system + history + user

        return full_context

    def get_response(self, message: Message) -> AIMessage:
        # TODO get history
        context = self.get_chat_context(message.chat.id, message)
        response = self.llm.invoke(context)

        self._store_history(message.chat.id, context[-1])
        self._store_history(message.chat.id, response)

        return response
