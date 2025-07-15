from abc import ABC, abstractmethod

from bourracho.models import ConversationMetadata, Message


class AbstractConversationStore(ABC):
    @abstractmethod
    def __init__(self, db_dir: str, conversation_id: str):
        """Initialize the store with a directory and conversation ID."""
        pass

    @abstractmethod
    def write_messages(self, messages: list[Message]) -> None:
        """Persist a list of messages to storage."""
        pass

    @abstractmethod
    def add_message(self, message: Message) -> None:
        """Add a single message to the conversation."""
        pass

    @abstractmethod
    def get_messages(self) -> list[Message]:
        """Retrieve all messages for the conversation."""
        pass

    @abstractmethod
    def get_users_ids(self) -> list[str]:
        """Retrieve all users for the conversation."""
        pass

    @abstractmethod
    def add_user_id(self, user_id: str) -> None:
        """Add a user to the conversation."""
        pass

    @abstractmethod
    def get_metadata(self) -> ConversationMetadata:
        """Retrieve metadata for the conversation."""
        pass

    @abstractmethod
    def write_metadata(self, metadata: ConversationMetadata) -> None:
        """Write conversation metadata to storage."""
        pass

    @abstractmethod
    def update_metadata(self, metadata_dict: dict) -> None:
        """Update conversation metadata with a dictionary of changes."""
        pass
