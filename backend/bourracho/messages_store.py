from typing import List

from loguru import logger
from pymongo import MongoClient

from bourracho import config
from bourracho.models import Message, React


class MessagesStore:
    def __init__(self, db_name: str):
        self.db_name = db_name
        auth_kgws = {}
        if config.MONGO_DB_PASSWORD and config.MONGO_DB_USERNAME:
            auth_kgws = {"username": config.MONGO_DB_USERNAME, "password": config.MONGO_DB_PASSWORD}
        self.client = MongoClient(config.MONGO_DB_URL, **auth_kgws)
        self.db = self.client[self.db_name]
        self.messages_collection = self.db[config.MESSAGES_COLLECTION]
        logger.debug("Initialized MessagesStore")

    def add_message(self, message: Message) -> None:
        Message.model_validate(message)
        self.messages_collection.insert_one(message.model_dump())

    def update_message(self, message: Message) -> None:
        self.messages_collection.update_one({"id": message.id}, {"$set": message.model_dump(exclude_unset=True)})

    def get_messages(self, conversation_id: str) -> List[Message]:
        return [Message.model_validate(m) for m in self.messages_collection.find({"conversation_id": conversation_id})]

    def get_message(self, message_id: str) -> Message:
        return Message.model_validate(self.messages_collection.find_one({"id": message_id}))

    def add_react(self, react: React, message_id: str) -> None:
        message_reacts = self.get_reacts(message_id=message_id)
        if any(r.issuer_id == react.issuer_id for r in message_reacts):
            logger.debug("Removing previous reaction for user %s", react.issuer_id)
            message_reacts.pop(message_reacts.index(next(r for r in message_reacts if r.issuer_id == react.issuer_id)))
        message_reacts.append(react)
        self.messages_collection.update_one(
            {"id": message_id},
            {"$set": {"reacts": [mr.model_dump() for mr in message_reacts]}},
        )
        logger.info(f"Added react {react} to message {message_id}.")

    def get_reacts(self, message_id: str) -> List[React]:
        message = self.messages_collection.find_one({"id": message_id})
        if not message:
            raise ValueError(f"Message {message_id} does not exist")
        return [React.model_validate(r) for r in message["reacts"]]
