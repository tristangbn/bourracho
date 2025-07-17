import json
import os
from os.path import join as pjoin

from loguru import logger

from bourracho.conversation_store.abstract_conversation_store import (
    AbstractConversationStore,
)
from bourracho.models import ConversationMetadata, JsonConversationStoreModel, Message, React


class JsonConversationStore(AbstractConversationStore):
    def __init__(self, db_dir: str, conversation_id: str):
        self.conversation_id = conversation_id
        self.db_dir = db_dir
        self.metadata_filepath = pjoin(self.db_dir, "metadata.json")
        self.users_ids_filepath = pjoin(self.db_dir, "users_ids.json")
        self.messages_filepath = pjoin(self.db_dir, "messages.json")

        logger.debug(f"Initializing JsonConversationStore at {db_dir}.")
        os.makedirs(self.db_dir, exist_ok=True)

    @classmethod
    def from_model(cls, model: JsonConversationStoreModel):
        return JsonConversationStore(model.db_dir, model.conversation_id)

    def write_messages(self, messages: list[Message]) -> None:
        with open(self.messages_filepath, "w") as f:
            json.dump([message.model_dump_json() for message in messages], f, ensure_ascii=True)

    def add_message(self, message: Message) -> None:
        Message.model_validate(message)
        conversation_messages = self.get_messages()
        logger.info(f"Adding message {message.id}.")
        conversation_messages.append(message)
        self.write_messages(conversation_messages)

    def get_messages(self) -> list[Message]:
        if not os.path.exists(self.messages_filepath):
            logger.debug("No messages to fetch.")
            return []
        with open(self.messages_filepath, "r") as f:
            return [Message.model_validate_json(message) for message in json.load(f)]

    def add_react(self, react: React, message_id: str) -> None:
        message = self.get_messages()
        message_ids = [message.id for message in message]
        if message_id not in message_ids:
            raise ValueError(f"Message with id {message_id} is not among registered messages.")
        message_index = message_ids.index(message_id)
        message[message_index].reacts.append(react)
        self.write_messages(message)
        logger.info(f"Added react {react} to message {message_id}.")

    def get_users_ids(self) -> list[str]:
        if not os.path.exists(self.users_ids_filepath):
            logger.debug("No user IDs registered for conversation")
            return []
        with open(self.users_ids_filepath) as f:
            return json.load(f)

    def add_user_id(self, user_id: str) -> None:
        existing_users_ids = self.get_users_ids()
        if user_id in existing_users_ids:
            logger.warning(f"A user with id {user_id} is already registered in conversation.")
            return
        new_users_ids = existing_users_ids + [user_id]
        with open(self.users_ids_filepath, "w") as f:
            json.dump(new_users_ids, f)
        logger.info(f"Successfully added user {user_id} to conversation.")

    def get_metadata(self) -> ConversationMetadata:
        if not os.path.exists(self.metadata_filepath):
            logger.debug("No metadata registered for conversation")
            return ConversationMetadata()
        with open(self.metadata_filepath) as f:
            return ConversationMetadata.model_validate(json.load(f))

    def write_metadata(self, metadata: ConversationMetadata):
        with open(self.metadata_filepath, "w") as f:
            json.dump(metadata.model_dump(), f)

    def update_metadata(self, metadata_dict: dict) -> None:
        conversation_metadata_dict = self.get_metadata().model_dump()
        conversation_metadata_dict.update(metadata_dict)
        conversation_metadata = ConversationMetadata(**conversation_metadata_dict)
        ConversationMetadata.model_validate(conversation_metadata)
        self.write_metadata(conversation_metadata)
