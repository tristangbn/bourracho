import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    pseudo: str | None = None
    location: str | None = None
    is_admin: bool = False


class React(BaseModel):
    emoji: str
    issuer: User


class Message(BaseModel):
    content: str
    issuer_id: str
    id: str = str(uuid.uuid4())
    timestamp: datetime = datetime.now()
    react: list[React] = []


class ConversationMetadata(BaseModel):
    name: str = ""
    id: str = str(uuid.uuid4())
    is_locked: bool = True


class Conversation(BaseModel):
    metadata: ConversationMetadata
    messages: list[Message] = []


class JsonMessageStore(BaseModel):
    type: Literal["json"] = "json"
    dir_path: str
    id: str = str(uuid.uuid4())
