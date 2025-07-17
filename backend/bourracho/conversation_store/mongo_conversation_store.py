from typing import List

from loguru import logger
from pymongo import MongoClient

from bourracho.conversation_store.abstract_conversation_store import AbstractConversationStore
from bourracho.models import ConversationMetadata, Message, MongoConversationStoreModel, React


class MongoConversationStore(AbstractConversationStore):
    def __init__(self, db_uri: str, conversation_id: str):
        self.conversation_id = conversation_id
        self.client = MongoClient(db_uri)
        self.db = self.client[self.conversation_id]
        self.messages_col = self.db[f"messages_{conversation_id}"]
        self.users_col = self.db[f"users_{conversation_id}"]
        self.metadata_col = self.db[f"metadata_{conversation_id}"]
        logger.debug(f"Initialized MongoConversationStore for conversation {conversation_id}")

    @classmethod
    def from_model(cls, model: MongoConversationStoreModel):
        return MongoConversationStore(model.db_uri, model.conversation_id)

    def write_messages(self, messages: List[Message]) -> None:
        self.messages_col.delete_many({})
        if messages:
            self.messages_col.insert_many([m.model_dump() for m in messages])

    def add_message(self, message: Message) -> None:
        Message.model_validate(message)
        self.messages_col.insert_one(message.model_dump())

    def get_messages(self) -> List[Message]:
        return [Message.model_validate(m) for m in self.messages_col.find()]

    def get_users_ids(self) -> List[str]:
        return [u["user_id"] for u in self.users_col.find()]

    def add_user_id(self, user_id: str) -> None:
        if self.users_col.find_one({"user_id": user_id}):
            logger.warning(f"A user with id {user_id} is already registered in conversation.")
            return
        self.users_col.insert_one({"user_id": user_id})
        logger.info(f"Successfully added user {user_id} to conversation.")

    def get_metadata(self) -> ConversationMetadata:
        doc = self.metadata_col.find_one()
        if not doc:
            logger.debug("No metadata registered for conversation")
            return ConversationMetadata()
        return ConversationMetadata.model_validate(doc)

    def write_metadata(self, metadata: ConversationMetadata) -> None:
        self.metadata_col.delete_many({})
        self.metadata_col.insert_one(metadata.model_dump())

    def update_metadata(self, metadata_dict: dict) -> None:
        doc = self.metadata_col.find_one() or {}
        doc.update(metadata_dict)
        conversation_metadata = ConversationMetadata(**doc)
        ConversationMetadata.model_validate(conversation_metadata)
        self.write_metadata(conversation_metadata)

    def add_react(self, react: React, message_id: str) -> None:
        result = self.messages_col.update_one(
            {"id": message_id},
            {"$push": {"reacts": react.model_dump()}},
        )
        if result.matched_count == 0:
            raise ValueError(f"Message with id {message_id} is not among registered messages.")
        logger.info(f"Added react {react} to message {message_id}.")
