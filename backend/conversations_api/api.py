import uuid
from datetime import datetime

from loguru import logger
from ninja import NinjaAPI, Schema
from pydantic import ValidationError

from bourracho.models import Conversation, Message, User, UserPayload
from bourracho.stores_registry import StoresRegistry
from conversations_api import config

registry = StoresRegistry(db_name=config.MONGO_DB_NAME)

api = NinjaAPI()


class ErrorResponse(Schema):
    error: str


@api.post("register/", response={200: dict, 500: ErrorResponse})
def register_user(request, user_credentials: UserPayload) -> User:
    logger.info("Received request to register user.")
    try:
        user = registry.register_user(username=user_credentials.username, password=user_credentials.password)
        logger.info(f"User registered with id: {user.id}")
        return 200, registry.get_user(user_id=user.id).model_dump(exclude="password_hash")
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {e}")
        return 500, {"error": str(e)}


@api.post("login/", response={200: User, 500: ErrorResponse})
def login(request, user_credentials: UserPayload):
    logger.info("Received request to login user.")
    try:
        user_id = registry.check_credentials(username=user_credentials.username, password=user_credentials.password)
        logger.info(f"User with id {user_id} logged in.")
        return 200, registry.get_user(user_id=user_id)
    except Exception as e:
        logger.error(f"Unexpected error during user login: {e}")
        return 500, {"error": str(e)}


@api.post("chat/", response={200: Conversation, 422: ErrorResponse, 500: ErrorResponse})
def create_conversation(request, conversation: Conversation):
    user_id = request.headers.get("user_id")
    logger.info("Received request to create conversation.")
    try:
        conversation_id = registry.create_conversation(user_id=user_id, conversation=conversation)
        logger.info(f"Conversation created with id: {conversation_id}")
        return 200, registry.get_conversation(conversation_id=conversation_id)
    except ValidationError as ve:
        logger.warning(f"Validation error during conversation creation: {ve}")
        return 422, {"error": f"Validation error: {ve}"}
    except Exception as e:
        logger.error(f"Unexpected error during conversation creation: {e}")
        return 500, {"error": str(e)}


@api.post("chat/{conversation_id}/join", response={200: Conversation, 500: ErrorResponse})
def join_conversation(request, conversation_id: str):
    user_id = request.headers.get("user_id")
    try:
        logger.info(f"Received request to join conversation {conversation_id} for user {user_id}.")
        registry.join_conversation(user_id=user_id, conversation_id=conversation_id)
        logger.info(f"User {user_id} joined conversation {conversation_id}.")
        return 200, registry.get_conversation(conversation_id=conversation_id)
    except Exception as e:
        logger.error(f"Unexpected error joining conversation {conversation_id} for user {user_id}: {e}")
        return 500, {"error": str(e)}


@api.post("chat/{conversation_id}/messages/", response={200: Message, 422: ErrorResponse, 500: ErrorResponse})
def post_message(request, conversation_id: str, message: Message):
    user_id = request.headers.get("user_id")
    try:
        logger.info(f"Received request to post message {message} to conversation {conversation_id}.")
        message.issuer_id = user_id
        message.id = message.id or str(uuid.uuid4())
        message.timestamp = message.timestamp or datetime.now()
        message = Message.model_validate(message)
        message.conversation_id = conversation_id
        registry.add_message(message=message)
        logger.info(f"Message posted to conversation {conversation_id}.")
        return 200, message
    except ValidationError as ve:
        logger.warning(f"Validation error posting message to {conversation_id}: {ve}")
        return 422, {"error": f"Validation error: {ve}"}
    except Exception as e:
        logger.error(f"Unexpected error posting message to {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.patch("chat/{conversation_id}", response={200: Conversation, 422: ErrorResponse, 500: ErrorResponse})
def patch_conversation(request, conversation_id: str, conversation: Conversation):
    try:
        logger.info(f"Received request to update metadata for conversation {conversation_id}.")
        conversation.id = conversation_id
        registry.update_conversation(conversation=conversation)
        logger.info(f"Metadata updated for conversation {conversation_id}.")
        return 200, registry.get_conversation(conversation_id=conversation_id)
    except ValidationError as ve:
        logger.warning(f"Validation error updating metadata for {conversation_id}: {ve}")
        return 422, {"error": f"Validation error: {ve}"}
    except Exception as e:
        logger.error(f"Unexpected error updating metadata for {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("chat/{conversation_id}/messages/", response={200: list[Message], 500: ErrorResponse})
def get_messages(request, conversation_id: str):
    try:
        logger.info(f"Received request to get messages for conversation {conversation_id}.")
        messages = registry.get_messages(conversation_id=conversation_id)
        logger.info(f"Fetched {len(messages)} messages for conversation {conversation_id}.")
        return 200, messages
    except Exception as e:
        logger.error(f"Error fetching messages for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("chat/{conversation_id}", response={200: Conversation, 500: ErrorResponse})
def get_conversation(request, conversation_id: str):
    try:
        logger.info(f"Received request to get metadata for conversation {conversation_id}.")
        conversation = registry.get_conversation(conversation_id=conversation_id)
        logger.info(f"Fetched metadata for conversation {conversation_id}.")
        return 200, conversation
    except Exception as e:
        logger.error(f"Error fetching metadata for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}


@api.get("/users", response={200: list[User], 500: ErrorResponse})
def get_users(request):
    logger.info("Received request to get users.")
    users_ids = request.GET.getlist("users_ids", "*")
    logger.info(f"Received request to get users for user_ids {users_ids}.")
    try:
        users = registry.get_users(user_ids=users_ids)
        logger.info(f"Fetched {len(users)} users for user_ids {users_ids}.")
        return 200, users
    except Exception as e:
        logger.error(f"Error fetching users for user_ids {users_ids}: {e}")
        return 500, {"error": str(e)}


@api.get("chat/", response={200: list[Conversation], 500: ErrorResponse})
def list_conversations(request):
    user_id = request.headers.get("user_id")
    try:
        logger.info("Received request to list all conversations.")
        conversations = registry.list_conversations(user_id=user_id)
        logger.info(f"Fetched {len(conversations)} conversations.")
        return 200, conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return 500, {"error": str(e)}


@api.patch("chat/{conversation_id}/messages", response={200: dict, 500: ErrorResponse})
def patch_message(request, conversation_id: str, message: Message):
    if not message.id:
        raise ValueError("Message id is required to update message")
    try:
        logger.info(f"Received request to update message {message} for conversation {conversation_id}.")
        message.issuer_id = request.headers.get("user_id")
        if message.reacts:
            registry.add_react(react=message.reacts[0], message_id=message.id)
            del message.reacts
        registry.update_message(message=message)
        logger.info(f"Message {message} updated for conversation {conversation_id}.")
        return 200, registry.get_message(message_id=message.id)
    except Exception as e:
        logger.error(f"Error updating message {message} for conversation {conversation_id}: {e}")
        return 500, {"error": str(e)}
