import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from loguru import logger
from pydantic import ValidationError

from bourracho.conversations_registry import ConversationsRegistry
from bourracho.models import ConversationMetadata, Message, React, User
from conversations_api import config

registry = ConversationsRegistry(
    conversations_registry_id=config.REGISTRY_ID,
    persistence_dir=config.REGISTRY_PERSISTENCE_DIR,
)


@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    logger.info("Received request to register user.")
    try:
        data = json.loads(request.body)
        user = User.model_validate(data)
        if not user.id:
            raise ValueError("User ID is required to register user.")
        registry.register_user(user=user)
        logger.info(f"User registered with id: {user.id}")
        return JsonResponse({"user_id": user.id})
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_conversation(request, user_id):
    logger.info("Received request to create conversation.")
    try:
        data = json.loads(request.body) if request.body else {}
        metadata = data.get("metadata")
        metadata = ConversationMetadata.model_validate(metadata)
        conversation_id = registry.add_conversation(conversation_metadata=metadata)
        logger.info(f"Conversation created with id: {conversation_id}")
        registry.add_user_id_to_conversation(conversation_id=conversation_id, user_id=user_id)
        logger.info(f"User {user_id} added to conversation {conversation_id}")
        return JsonResponse({"conversation_id": conversation_id})
    except ValidationError as ve:
        logger.warning(f"Validation error during conversation creation: {ve}")
        return JsonResponse({"error": f"Validation error: {ve}"}, status=422)
    except Exception as e:
        logger.error(f"Unexpected error during conversation creation: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def join_conversation(request, user_id):
    try:
        data = json.loads(request.body) if request.body else {}
        conversation_id = data.get("conversation_id")
        logger.info(f"Received request to join conversation {conversation_id} for user {user_id}.")
        registry.join_conversation(user_id=user_id, conversation_id=conversation_id)
        logger.info(f"User {user_id} joined conversation {conversation_id}.")
        return JsonResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Unexpected error joining conversation {conversation_id} for user {user_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def post_message(request, user_id, conversation_id):
    try:
        logger.info(f"Received request to post message to conversation {conversation_id}.")
        data = json.loads(request.body)
        message = data["message"]
        message["issuer_id"] = user_id
        message = Message.model_validate(message)
        registry.add_message(conversation_id=conversation_id, message=message)
        logger.info(f"Message posted to conversation {conversation_id}.")
        return JsonResponse({"status": "success"})
    except ValidationError as ve:
        logger.warning(f"Validation error posting message to {conversation_id}: {ve}")
        return JsonResponse({"error": f"Validation error: {ve}"}, status=422)
    except Exception as e:
        logger.error(f"Unexpected error posting message to {conversation_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def post_metadata(request, user_id, conversation_id):
    try:
        logger.info(f"Received request to update metadata for conversation {conversation_id}.")
        data = json.loads(request.body)
        metadata = data["metadata"]
        registry.update_metadata(conversation_id=conversation_id, metadata_dict=metadata)
        logger.info(f"Metadata updated for conversation {conversation_id}.")
        return JsonResponse({"status": "success"})
    except ValidationError as ve:
        logger.warning(f"Validation error updating metadata for {conversation_id}: {ve}")
        return JsonResponse({"error": f"Validation error: {ve}"}, status=422)
    except Exception as e:
        logger.error(f"Unexpected error updating metadata for {conversation_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_messages(request, user_id, conversation_id):
    try:
        logger.info(f"Received request to get messages for conversation {conversation_id}.")
        messages = registry.get_messages(conversation_id=conversation_id)
        logger.info(f"Fetched {len(messages)} messages for conversation {conversation_id}.")
        return JsonResponse({"messages": [message.model_dump_json() for message in messages]})
    except Exception as e:
        logger.error(f"Error fetching messages for conversation {conversation_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_metadata(request, user_id, conversation_id):
    try:
        logger.info(f"Received request to get metadata for conversation {conversation_id}.")
        metadata = registry.get_metadata(conversation_id=conversation_id)
        logger.info(f"Fetched metadata for conversation {conversation_id}.")
        return JsonResponse({"metadata": metadata.model_dump_json()})
    except Exception as e:
        logger.error(f"Error fetching metadata for conversation {conversation_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_users(request, user_id, conversation_id):
    try:
        logger.info(f"Received request to get users for conversation {conversation_id}.")
        users = registry.get_users(conversation_id=conversation_id)
        logger.info(f"Fetched {len(users)} users for conversation {conversation_id}.")
        return JsonResponse({"users": [user.model_dump_json() for user in users]})
    except Exception as e:
        logger.error(f"Error fetching users for conversation {conversation_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def list_conversations(request, user_id):
    try:
        logger.info("Received request to list all conversations.")
        conversations_metadata = registry.list_conversations(user_id=user_id)
        result = [meta.model_dump_json() for meta in conversations_metadata]
        logger.info(f"Fetched {len(result)} conversations.")
        return JsonResponse({"conversations": result})
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def post_react(request, user_id, conversation_id):
    try:
        data = json.loads(request.body)
        message_id = data.get("message_id")
        react = React.model_validate(data.get("react"))
        logger.info(f"Received request to post react for conversation {conversation_id}.")
        registry.add_react(user_id=user_id, conversation_id=conversation_id, react=react, message_id=message_id)
        logger.info(f"React posted for conversation {conversation_id}.")
        return JsonResponse({"react": react.model_dump_json()})
    except Exception as e:
        logger.error(f"Error posting react for conversation {conversation_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)
