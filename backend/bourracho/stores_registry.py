import random
import string
import uuid
from datetime import datetime

from loguru import logger

from bourracho.conversations_store import ConversationsStore
from bourracho.messages_store import MessagesStore
from bourracho.models import Conversation, Message, React, User
from bourracho.users_store import UsersStore


class StoresRegistry:
    def __init__(self, db_name: str):
        self.db_name: str = db_name
        """Name of the database"""
        self.conversations_store: ConversationsStore = ConversationsStore(self.db_name)
        """Dict containing for each conversation an entry conversation_id: ConversationStore"""
        self.messages_store: MessagesStore = MessagesStore(self.db_name)
        """Dict containing for each conversation an entry conversation_id: ConversationStoresModel"""
        self.users_store: UsersStore = UsersStore(self.db_name)
        """Dict containing for each user an entry user_id: User"""

    def register_user(self, username: str, password: str) -> User:
        user = self.users_store.get_new_user(username, password)
        self.users_store.add_user(user=user)
        return user

    def check_credentials(self, username: str, password: str) -> str | None:
        return self.users_store.check_credentials(username=username, password=password)

    def get_user(self, user_id: str) -> User | None:
        return self.users_store.get_user(user_id=user_id)

    def get_users(self, user_ids: list[str]) -> list[User]:
        return self.users_store.get_users(user_ids=user_ids)

    def create_conversation(
        self,
        user_id: str,
        conversation: Conversation,
    ) -> str:
        if not user_id:
            raise ValueError("User ID is required to create conversation.")
        conversation.id = conversation.id or "".join(random.choices(string.ascii_letters + string.digits, k=6))
        self.conversations_store.add_conversation(conversation=conversation)
        self.conversations_store.add_user_id_to_conversation(conversation_id=conversation.id, user_id=user_id)
        return conversation.id

    def join_conversation(self, user_id: str, conversation_id: str) -> None:
        if not user_id:
            raise ValueError("User ID is required to join conversation.")
        if not conversation_id:
            raise ValueError("Conversation ID is required to join conversation.")
        self.conversations_store.add_user_id_to_conversation(conversation_id=conversation_id, user_id=user_id)

    def list_conversations(self, user_id: str) -> list[Conversation]:
        if not user_id:
            raise ValueError("User ID is required to list conversations.")
        conversations = self.conversations_store.get_conversations(user_id=user_id)
        return conversations

    def update_conversation(self, conversation: Conversation) -> None:
        self.conversations_store.update_conversation(conversation)

    def add_message(self, message: Message):
        if message.issuer_id not in self.conversations_store.get_user_ids(message.conversation_id):
            raise ValueError(
                f"User {message.issuer_id} is not among registered user of conversation {message.conversation_id}"
            )
        message.id = message.id or str(uuid.uuid4())
        message.timestamp = message.timestamp or datetime.now()
        self.messages_store.add_message(message=message)
        logger.info(f"Message {message} successfully added.")

    def update_message(self, message: Message):
        self.messages_store.update_message(message=message)
        logger.info(f"Message {message} successfully updated.")

    def add_react(self, react: React, message_id: str):
        self.messages_store.add_react(react=react, message_id=message_id)

    def get_messages(self, conversation_id: str) -> list[Message]:
        return self.messages_store.get_messages(conversation_id=conversation_id)

    def get_message(self, message_id: str) -> Message:
        return self.messages_store.get_message(message_id=message_id)

    def get_conversation(self, conversation_id: str) -> Conversation:
        return self.conversations_store.get_conversation(conversation_id=conversation_id)
