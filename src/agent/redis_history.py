import logging
import time
from typing import Iterable, List
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from redis import Redis


class RedisHistoryManager:
    def __init__(self, redis_db: Redis, prefix: str = "history"):
        self.redis_db = redis_db
        self.prefix = prefix
        self.logger = logging.getLogger("chocolate-joe")

    def store_message(self, message: BaseMessage, chat_id: int, ttl: int):
        message_id = uuid4().hex
        key = f"{self.prefix}:{chat_id}:{message_id}"
        value = {
            "content": message.text,
            "role": "ai" if isinstance(message, HumanMessage) else "user",
            "timestamp": int(time.time() * 1000),
        }

        try:
            self.redis_db.json().set(key, ".", value)
            self.redis_db.expire(key, ttl)
            self.logger.info(f"Stored message {message_id} for chat {chat_id}")

        except Exception as e:
            self.logger.error(f"Failed to store message: {e}")

    def get_chat_history(self, chat_id: int) -> List[BaseMessage]:
        history = []
        keys = self.redis_db.keys(f"{self.prefix}:{chat_id}:*")

        if not keys or not isinstance(keys, Iterable):
            self.logger.info(
                f"Retrieved {len(history)} messages for chat {chat_id}."
            )
            return history

        for key in keys:
            message: dict = self.redis_db.json().get(key)  # pyright: ignore
            if not message:
                continue
            history.append(message)

        history.sort(key=lambda x: x["timestamp"])

        for idx, message in enumerate(history):
            if message["role"] == "user":
                history[idx] = HumanMessage(content=message["content"])
            elif message["role"] == "ai":
                history[idx] = AIMessage(content=message["content"])

        self.logger.info(
            f"Retrieved {len(history)} messages for chat {chat_id}."
        )
        return history
