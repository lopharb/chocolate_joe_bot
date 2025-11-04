from typing import List

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
)
from langchain_groq.chat_models import ChatGroq


class LCModel(ChatGroq):
    def __init__(self):
        pass

    def get_response(self, context: List[BaseMessage]) -> AIMessage:
        response = self.invoke(context)

        return response
