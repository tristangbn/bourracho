import uuid
from datetime import datetime
from typing import Annotated, Literal

import emoji as emj
from pydantic import AfterValidator, BaseModel, field_serializer


class User(BaseModel):
    id: str
    name: str
    pseudo: str | None = None
    location: str | None = None
    is_admin: bool = False


class React(BaseModel):
    emoji: Annotated[str, AfterValidator(lambda s: emj.emojize(s))]
    issuer_id: str

    @field_serializer("emoji")
    def serialize_emoji(self, emoji: str):
        return emj.emojize(emoji)


class Message(BaseModel):
    content: str
    issuer_id: str
    id: str = str(uuid.uuid4())
    timestamp: datetime = datetime.now()
    reacts: list[React] = []


class ConversationMetadata(BaseModel):
    name: str = ""
    id: str | None = None
    is_locked: bool = True


class Conversation(BaseModel):
    metadata: ConversationMetadata
    messages: list[Message] = []


class JsonMessageStore(BaseModel):
    type: Literal["json"] = "json"
    dir_path: str
    id: str = str(uuid.uuid4())
