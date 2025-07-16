import json
import os
import random
import string
from os.path import join as pjoin
from typing import Literal

from loguru import logger

from bourracho.conversation_store.abstract_conversation_store import (
    AbstractConversationStore,
)
from bourracho.conversation_store.json_conversation_store import JsonConversationStore
from bourracho.models import ConversationMetadata, Message, React, User


class ConversationsRegistry:
    def __init__(self, conversations_registry_id: str, persistence_dir: str, users: dict[str, User] | None = None):
        self.id: str = conversations_registry_id
        """"Unique identifier for the conversations registry"""
        self.persistence_dir: str = pjoin(persistence_dir, f"registry_id={self.id}")
        """Dir path to were every information about conversations should be stored"""
        self.conversation_stores: dict[str, AbstractConversationStore] = {}
        """Dict containing for each conversation an entry conversation_id: MessageStore"""
        self.users: dict[str, User] = users or {}
        """Dict containing for each user an entry user_id: User"""

        self.conversations_registry_filepath = pjoin(self.persistence_dir, "information.json")
        os.makedirs(self.persistence_dir, exist_ok=True)
        if not os.path.exists(self.conversations_registry_filepath):
            self.serialize()
        else:
            self.load_from_json_file()

    def load_from_json_file(self):
        logger.info(f"Reloading conversation registry from file {self.conversations_registry_filepath}")
        with open(self.conversations_registry_filepath) as f:
            persisted_conversations_registry = json.load(f)
        if not persisted_conversations_registry:
            return
        logger.debug(f"Persisted file: {persisted_conversations_registry}")
        logger.info(f"Reloading conversations : {persisted_conversations_registry['conversation_stores'].keys()}")
        self.conversation_stores = {
            conversation_id: JsonConversationStore(**conversations_stores)
            for conversation_id, conversations_stores in persisted_conversations_registry["conversation_stores"].items()
        }
        self.users = {
            user_id: User.model_validate_json(user)
            for user_id, user in persisted_conversations_registry["users"].items()
        }

    def serialize(self) -> None:
        logger.info(f"Serializing conversation registry to file {self.conversations_registry_filepath}")
        d = {
            "id": self.id,
            "persistence_dir": self.persistence_dir,
            "conversation_stores": {k: v.dump() for k, v in self.conversation_stores.items()},
            "users": {k: v.model_dump_json() for k, v in self.users.items()},
        }
        with open(self.conversations_registry_filepath, "w") as f:
            json.dump(d, f)

    def register_user(self, user: User):
        if not user.id:
            raise ValueError("User ID is required to register user.")
        if user.id in self.users:
            logger.warning(f"User with id {user.id} is already registered in conversation.")
            return
        self.users[user.id] = user
        self.serialize()
        logger.success(f"User {user} successfully registered.")

    def get_user(self, user_id: str) -> User:
        if user_id not in self.users:
            raise ValueError(f"User with id {user_id} is not among registered users.")
        return self.users[user_id]

    def create_conversation(self, user_id: str, metadata: ConversationMetadata) -> str:
        if not user_id:
            raise ValueError("User ID is required to create conversation.")
        metadata = ConversationMetadata.model_validate(metadata)
        conversation_id = self.add_conversation(conversation_metadata=metadata)
        self.add_user_id_to_conversation(conversation_id=conversation_id, user_id=user_id)
        return conversation_id

    def join_conversation(self, user_id: str, conversation_id: str) -> None:
        if not user_id:
            raise ValueError("User ID is required to join conversation.")
        if not conversation_id:
            raise ValueError("Conversation ID is required to join conversation.")
        self.add_user_id_to_conversation(conversation_id=conversation_id, user_id=user_id)

    def list_conversations(self, user_id: str) -> list[ConversationMetadata]:
        if not user_id:
            raise ValueError("User ID is required to list conversations.")
        conversations = [
            conversation_store.get_metadata()
            for conversation_store in self.conversation_stores.values()
            if user_id in conversation_store.get_users_ids()
        ]
        logger.info(f"Loaded {[conversation.name for conversation in conversations]} conversations for user {user_id}")
        return conversations

    def add_conversation(
        self,
        conversation_metadata: ConversationMetadata | dict,
        conversation_store_type: Literal["json"] = "json",
    ) -> str:
        if conversation_store_type != "json":
            raise NotImplementedError("Only json Message store is implemented yet.")

        conversation_metadata = conversation_metadata or ConversationMetadata()
        conversation_metadata.id = conversation_metadata.id or "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        if conversation_metadata.id in self.conversation_stores:
            raise ValueError(
                f"Conversation with id {conversation_metadata.id} is already among implemented conversations."
            )

        conversation_store = JsonConversationStore(
            db_dir=f"{self.persistence_dir}/{conversation_metadata.id}", conversation_id=conversation_metadata.id
        )
        self.conversation_stores[conversation_metadata.id] = conversation_store
        conversation_store.write_metadata(conversation_metadata)
        self.serialize()
        logger.success(f"Conversation {conversation_metadata} successfully added.")
        return conversation_metadata.id

    def get_all_conversations(self):
        logger.info(f"Returning all conversations: {self.conversation_stores.keys()}")
        return self.conversation_stores

    def add_message(self, message: Message, conversation_id: str):
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        self.conversation_stores[conversation_id].add_message(message)
        logger.success(f"Message {message} successfully added to conversation {conversation_id}.")

    def add_react(self, react: React, conversation_id: str, message_id: str):
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        self.conversation_stores[conversation_id].add_react(react, message_id=message_id)
        logger.success(f"React {react} successfully added to conversation {conversation_id}.")

    def add_user_id_to_conversation(self, user_id: str, conversation_id: str):
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        self.conversation_stores[conversation_id].add_user_id(user_id)
        logger.success(f"User {user_id} successfully added to conversation {conversation_id}.")

    def get_messages(
        self,
        conversation_id: str,
    ) -> list[Message]:
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        return self.conversation_stores[conversation_id].get_messages()

    def update_metadata(
        self,
        conversation_id: str,
        metadata_dict: dict,
    ) -> None:
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        self.conversation_stores[conversation_id].update_metadata(metadata_dict)

    def get_metadata(self, conversation_id: str) -> ConversationMetadata:
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        return self.conversation_stores[conversation_id].get_metadata()

    def get_users(self, conversation_id: str) -> list[User]:
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        return self.conversation_stores[conversation_id].get_users()
