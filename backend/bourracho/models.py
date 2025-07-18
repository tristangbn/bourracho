from datetime import datetime
from typing import Annotated, Literal

import emoji as emj
from pydantic import AfterValidator, BaseModel, field_serializer


class UserPayload(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: str
    username: str
    password_hash: str
    pseudo: str | None = None
    location: str | None = None


class React(BaseModel):
    emoji: Annotated[str, AfterValidator(lambda s: emj.emojize(s))]
    issuer_id: str | None = None

    @field_serializer("emoji")
    def serialize_emoji(self, emoji: str):
        return emj.emojize(emoji)


class Message(BaseModel):
    id: str = None
    content: str
    conversation_id: str
    issuer_id: str
    timestamp: datetime = None
    reacts: list[React] = []


class Conversation(BaseModel):
    id: str = None
    users_ids: list[str] = []
    name: str = "Name me 😘"
    is_locked: bool = True


class MongoConversationStoreModel(BaseModel):
    type: Literal["mongo_db"] = "mongo_db"
    db_uri: str
    conversation_id: str | None = None
