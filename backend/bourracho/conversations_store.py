from typing import List

from loguru import logger
from pymongo import MongoClient

from bourracho import config
from bourracho.models import Conversation


class ConversationsStore:
    def __init__(self, db_name: str):
        self.db_name = db_name
        auth_kgws = {}
        if config.MONGO_DB_PASSWORD and config.MONGO_DB_USERNAME:
            auth_kgws = {"username": config.MONGO_DB_USERNAME, "password": config.MONGO_DB_PASSWORD}
        self.client = MongoClient(config.MONGO_DB_URL, **auth_kgws)
        self.db = self.client[self.db_name]
        self.conversations_collection = self.db[config.CONVERSATIONS_COLLECTION]
        logger.debug("Initialized ConversationsStore")

    def add_conversation(self, conversation: Conversation) -> None:
        Conversation.model_validate(conversation)
        self.conversations_collection.insert_one(conversation.model_dump())

    def get_conversation(self, conversation_id: str) -> Conversation:
        return Conversation.model_validate(self.conversations_collection.find_one({"id": conversation_id}))

    def get_conversations(self, user_id: str) -> List[Conversation]:
        return [
            Conversation.model_validate(c)
            for c in self.conversations_collection.find({"users_ids": {"$in": [user_id]}})
        ]

    def get_user_ids(self, conversation_id: str) -> list[str]:
        return self.conversations_collection.find_one({"id": conversation_id}, {"users_ids": 1})["users_ids"]

    def add_user_id_to_conversation(self, user_id: str, conversation_id: str) -> None:
        self.conversations_collection.update_one({"id": conversation_id}, {"$addToSet": {"users_ids": user_id}})
        logger.info(f"Succesfully added user {user_id} to conversation {conversation_id}")

    def update_conversation(self, conversation: Conversation) -> None:
        self.conversations_collection.update_one(
            {"id": conversation.id}, {"$set": conversation.model_dump(exclude_unset=True)}
        )
        logger.info(f"Succesfully updated conversation {conversation.id}")
