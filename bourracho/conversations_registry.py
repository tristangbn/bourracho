import json
import os
from os.path import join as pjoin
from typing import Literal

from loguru import logger

from bourracho.conversation_store.abstract_conversation_store import (
    AbstractConversationStore,
)
from bourracho.conversation_store.json_conversation_store import JsonConversationStore
from bourracho.models import ConversationMetadata, Message, User


class ConversationsRegistry:
    def __init__(self, conversations_registry_id: str, persistence_dir: str):
        self.id: str = conversations_registry_id
        """"Unique identifier for the conversations registry"""
        self.persistence_dir: str = persistence_dir
        """Dir path to were every information about conversations should be stored"""
        self.conversation_stores: dict[str, AbstractConversationStore] = {}
        """Dict containing for each conversation an entry conversation_id: MessageStore"""

        self.conversations_registry_filepath = pjoin(self.persistence_dir, f"registry_id={self.id}.json")
        os.makedirs(self.persistence_dir, exist_ok=True)
        if not os.path.exists(self.conversations_registry_filepath):
            with open(self.conversations_registry_filepath, "w") as f:
                json.dump({}, f)
        else:
            self.load_from_json_file()

    def load_from_json_file(self):
        logger.info(f"Reloading conversation registry from file {self.conversations_registry_filepath}")
        with open(self.conversations_registry_filepath) as f:
            persisted_conversations_registry = json.load(f)
        logger.debug(f"Persisted file: {persisted_conversations_registry}")
        logger.info(f"Reloading conversations : {persisted_conversations_registry.keys()}")
        self.conversation_stores = {
            conversation_id: JsonConversationStore(**conversations_stores)
            for conversation_id, conversations_stores in persisted_conversations_registry.items()
        }

    def add_conversation(
        self,
        conversation_metadata: ConversationMetadata | dict,
        conversation_store_type: Literal["json"] = "json",
    ) -> str:
        if conversation_store_type != "json":
            raise NotImplementedError("Only json Message store is implemented yet.")

        conversation_metadata = conversation_metadata or ConversationMetadata()
        if conversation_metadata.id in self.conversation_stores:
            raise ValueError(
                f"Conversation with id {conversation_metadata.id} is already among implemented conversations."
            )

        conversation_store = JsonConversationStore(
            db_dir=self.persistence_dir, conversation_id=conversation_metadata.id
        )
        self.conversation_stores[conversation_metadata.id] = conversation_store
        self.serialize()
        return conversation_metadata.id

    def serialize(self) -> None:
        with open(self.conversations_registry_filepath, "w") as f:
            json.dump({k: v.dump() for k, v in self.conversation_stores.items()}, f)

    def get_all_conversations(self):
        return self.conversation_stores

    def add_message(self, message: Message, conversation_id: str):
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        self.conversation_stores[conversation_id].add_message(message)

    def add_user(self, user: User, conversation_id: str):
        if conversation_id not in self.conversation_stores:
            raise ValueError(f"Conversation with id {conversation_id} is not among registered conversations.")
        self.conversation_stores[conversation_id].add_user(user)

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
