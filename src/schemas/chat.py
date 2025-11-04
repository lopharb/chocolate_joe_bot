from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: str
    session_id: str
    sender: str
    content: str
    timestamp: str
