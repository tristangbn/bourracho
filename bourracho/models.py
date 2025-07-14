import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator


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
    id: str
    content: str
    timestamp: datetime
    issuer: User
    react: list[React] = []


class ConversationMetadata(BaseModel):
    name: str = ""
    id: str = str(uuid.uuid4())
    users: list[User] = []
    messages_count: int = 0
    is_locked: bool = True


class Conversation(BaseModel):
    metadata: ConversationMetadata
    messages: list[Message] = []


class JsonMessageStore(BaseModel):
    type: Literal["json"] = "json"
    id: str
    dir_path: str


class MessageStoreRegistry(BaseModel):
    id: str
    message_registry_filepath: str


class AddConversationOperation(BaseModel):
    op_type: Literal["add"] = "add"
    conversation_registry_id: str
    conversation: Conversation


class GetAllConversationsOperation(BaseModel):
    op_type: Literal["get_all"] = "get_all"
    conversation_registry_id: str


ConversationsRegistryOperation = Annotated[
    AddConversationOperation | GetAllConversationsOperation, Discriminator("op_type")
]
