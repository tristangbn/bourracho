import json
import os
from os.path import join as pjoin

from loguru import logger

from bourracho.conversation_store.abstract_conversation_store import (
    AbstractConversationStore,
)
from bourracho.models import ConversationMetadata, Message, User


class JsonConversationStore(AbstractConversationStore):
    def __init__(self, db_dir: str, conversation_id: str):
        self.conversation_id = conversation_id
        self.db_dir = db_dir
        self.metadata_filepath = pjoin(self.db_dir, "metadata.json")
        self.users_filepath = pjoin(self.db_dir, "users.json")
        self.messages_filepath = pjoin(self.db_dir, "messages.json")

        logger.debug(f"Initializing JsonConversationStore at {db_dir}.")
        os.makedirs(self.db_dir, exist_ok=True)

    def dump(self) -> dict:
        return {
            "db_dir": self.db_dir,
            "conversation_id": self.conversation_id,
        }

    def write_messages(self, messages: list[Message]) -> None:
        with open(self.messages_filepath, "w") as f:
            json.dump([message.model_dump_json() for message in messages], f)

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

    def get_users(self) -> list[User]:
        if not os.path.exists(self.users_filepath):
            logger.debug("No user registered for conversation")
            return []
        with open(self.users_filepath) as f:
            return [User.model_validate_json(user) for user in json.load(f)]

    def add_user(self, user: User) -> None:
        User.model_validate(user)
        existing_users = self.get_users()
        if any(existing_user.id == user.id for existing_user in existing_users):
            raise ValueError(f"A user with id {user.id} is already registered in conversation.")
        new_users = existing_users + [user]
        with open(self.users_filepath, "w") as f:
            json.dump([new_user.model_dump_json() for new_user in new_users], f)
        logger.info(f"Successfully added user {user} to conversation.")

    def get_metadata(self) -> ConversationMetadata:
        if not os.path.exists(self.metadata_filepath):
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
