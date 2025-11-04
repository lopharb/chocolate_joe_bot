from typing import List, Literal

import instructor
from groq import Groq
from pydantic import BaseModel, Field

client = instructor.from_groq(Groq())


MESSAGE_TYPES = Literal["CASUAL_CHAT", "COMMAND", "SPECIFIC_QUESTION", "FOLLOW_UP"]


class MultiClassPrediction(BaseModel):
    labels: List[MESSAGE_TYPES] = Field(
        ...,
        description="Only select the labels that apply to the message.",
    )


def multi_classify(message: str) -> MultiClassPrediction:
    return client.chat.completions.create(
        model="openai/gpt-oss-120b",
        response_model=MultiClassPrediction,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a chat moderator. You need to label all the messages based on their type. Only use the provided labels.",
            },
            {
                "role": "user",
                "content": message,
            },
        ],
    )  # type: ignore


if __name__ == "__main__":
    ticket = "как дела"
    prediction = multi_classify(ticket)
    print("input:", ticket)
    # > input: My account is locked and I can't access my billing info.
    print("labels:", MESSAGE_TYPES)
    # > labels: typing.Literal['ACCOUNT', 'BILLING', 'GENERAL_QUERY']
    print("prediction:", prediction)
    # > prediction: labels=['ACCOUNT', 'BILLING']
