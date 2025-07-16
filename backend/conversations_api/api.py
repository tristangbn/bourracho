import uuid
from datetime import datetime
from typing import Any, Dict

from loguru import logger
from ninja import NinjaAPI, Schema
from pydantic import ValidationError

from bourracho.conversations_registry import ConversationsRegistry
from bourracho.models import ConversationMetadata, Message, React, User
from conversations_api import config

registry = ConversationsRegistry(
    conversations_registry_id=config.REGISTRY_ID,
    persistence_dir=config.REGISTRY_PERSISTENCE_DIR,
)

api = NinjaAPI()


class ErrorResponse(Schema):
    error: str


@api.post("auth/", response={200: Dict[str, str], 500: ErrorResponse})
def register_user(request, payload: User):
    logger.info("Received request to register user.")
    try:
        user = User.model_validate(payload)
        if not user.id:
            raise ValueError("User ID is required to register user.")
        registry.register_user(user=user)
        logger.info(f"User registered with id: {user.id}")
        return {"user_id": user.id}
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {e}")
        return 500, {"error": str(e)}


@api.post("conversations/{user_id}/create", response={200: Dict[str, str], 422: ErrorResponse, 500: ErrorResponse})
def create_conversation(request, user_id: str, metadata: ConversationMetadata):
    logger.info("Received request to create conversation.")
    try:
        conversation_id = registry.add_conversation(conversation_metadata=metadata)
        logger.info(f"Conversation created with id: {conversation_id}")
        registry.add_user_id_to_conversation(conversation_id=conversation_id, user_id=user_id)
        logger.info(f"User {user_id} added to conversation {conversation_id}")
        return {"conversation_id": conversation_id}
    except ValidationError as ve:
        logger.warning(f"Validation error during conversation creation: {ve}")
        return 422, {"error": f"Validation error: {ve}"}
    except Exception as e:
        logger.error(f"Unexpected error during conversation creation: {e}")
        return 500, {"error": str(e)}


@api.post("conversations/{user_id}/join", response={200: Dict[str, str], 500: ErrorResponse})
def join_conversation(request, user_id: str, conversation_id: str):
    try:
        logger.info(f"Received request to join conversation {conversation_id} for user {user_id}.")
        registry.join_conversation(user_id=user_id, conversation_id=conversation_id)
        logger.info(f"User {user_id} joined conversation {conversation_id}.")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Unexpected error joining conversation {conversation_id} for user {user_id}: {e}")
        return 500, {"error": str(e)}


@api.post(
    "messages/{user_id}/{conversation_id}", response={200: Dict[str, str], 422: ErrorResponse, 500: ErrorResponse}
)
def post_message(request, user_id: str, conversation_id: str, message: Message):
    try:
        logger.info(f"Received request to post message {message} to conversation {conversation_id}.")
        message.issuer_id = user_id
        message.id = message.id or str(uuid.uuid4())
        message.timestamp = message.timestamp or datetime.now()
        message = Message.model_validate(message)
        registry.add_message(conversation_id=conversation_id, message=message)
        logger.info(f"Message posted to conversation {conversation_id}.")
        return {"status": "success"}
    except ValidationError as ve:
        logger.warning(f"Validation error posting message to {conversation_id}: {ve}")
        return 422, {"error": f"Validation error: {ve}"}
    except Exception as e:
        logger.error(f"Unexpected error posting message to {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.post(
    "metadata/{user_id}/{conversation_id}", response={200: Dict[str, str], 422: ErrorResponse, 500: ErrorResponse}
)
def post_metadata(request, user_id: str, conversation_id: str, metadata: ConversationMetadata):
    try:
        logger.info(f"Received request to update metadata for conversation {conversation_id}.")
        registry.update_metadata(conversation_id=conversation_id, metadata_dict=metadata.model_dump())
        logger.info(f"Metadata updated for conversation {conversation_id}.")
        return {"status": "success"}
    except ValidationError as ve:
        logger.warning(f"Validation error updating metadata for {conversation_id}: {ve}")
        return 422, {"error": f"Validation error: {ve}"}
    except Exception as e:
        logger.error(f"Unexpected error updating metadata for {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("messages/{user_id}/{conversation_id}/get", response={200: Dict[str, Any], 500: ErrorResponse})
def get_messages(request, user_id: str, conversation_id: str):
    try:
        logger.info(f"Received request to get messages for conversation {conversation_id}.")
        messages = registry.get_messages(conversation_id=conversation_id)
        logger.info(f"Fetched {len(messages)} messages for conversation {conversation_id}.")
        return {"messages": [message.model_dump_json() for message in messages]}
    except Exception as e:
        logger.error(f"Error fetching messages for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("metadata/{user_id}/{conversation_id}/get", response={200: Dict[str, Any], 500: ErrorResponse})
def get_metadata(request, user_id: str, conversation_id: str):
    try:
        logger.info(f"Received request to get metadata for conversation {conversation_id}.")
        metadata = registry.get_metadata(conversation_id=conversation_id)
        logger.info(f"Fetched metadata for conversation {conversation_id}.")
        return {"metadata": metadata.model_dump_json()}
    except Exception as e:
        logger.error(f"Error fetching metadata for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("users/{user_id}/{conversation_id}/get", response={200: Dict[str, Any], 500: ErrorResponse})
def get_users(request, user_id: str, conversation_id: str):
    try:
        logger.info(f"Received request to get users for conversation {conversation_id}.")
        users = registry.get_users(conversation_id=conversation_id)
        logger.info(f"Fetched {len(users)} users for conversation {conversation_id}.")
        return {"users": [user.model_dump_json() for user in users]}
    except Exception as e:
        logger.error(f"Error fetching users for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("conversations/{user_id}/get", response={200: Dict[str, Any], 500: ErrorResponse})
def list_conversations(request, user_id: str):
    try:
        logger.info("Received request to list all conversations.")
        conversations_metadata = registry.list_conversations(user_id=user_id)
        result = [meta.model_dump_json() for meta in conversations_metadata]
        logger.info(f"Fetched {len(result)} conversations.")
        return {"conversations": result}
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return 500, {"error": str(e)}


@api.post("react/{user_id}/{conversation_id}", response={200: Dict[str, Any], 500: ErrorResponse})
def post_react(request, user_id: str, conversation_id: str, message_id: str, react: React):
    try:
        logger.info(f"Received request to post react for conversation {conversation_id}.")
        react.issuer_id = user_id
        registry.add_react(
            conversation_id=conversation_id,
            message_id=message_id,
            react=react,
        )
        logger.info(f"React posted for conversation {conversation_id}.")
        return {"react": react.model_dump_json()}
    except Exception as e:
        logger.error(f"Error posting react for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}
