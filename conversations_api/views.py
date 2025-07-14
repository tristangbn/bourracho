import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from loguru import logger
from pydantic import ValidationError

from bourracho.conversations_registry import ConversationsRegistry
from bourracho.models import ConversationMetadata, Message, User
from conversations_api import config

registry = ConversationsRegistry(
    conversations_registry_id="api1",
    persistence_dir=config.REGISTRY_PERSISTENCE_DIR,
)


@csrf_exempt
@require_http_methods(["POST"])
def create_conversation(request):
    try:
        data = json.loads(request.body) if request.body else {}
        metadata = data.get("metadata")
        metadata = ConversationMetadata.model_validate(metadata)
        conversation_id = registry.add_conversation(metadata)
        return JsonResponse({"conversation_id": conversation_id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def post_message(request, conversation_id):
    try:
        data = json.loads(request.body)
        message = data["message"]
        message = Message.model_validate(message)
        registry.add_message(conversation_id=conversation_id, message=message)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def post_user(request, conversation_id):
    try:
        data = json.loads(request.body)
        user = data["user"]
        user = User.model_validate(user)
    except ValidationError as e:
        logger.error(f"Validation error for user : {user}")
        raise e
    try:
        registry.add_user(conversation_id=conversation_id, user=user)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def post_metadata(request, conversation_id):
    try:
        data = json.loads(request.body)
        metadata = data["metadata"]
        registry.update_metadata(conversation_id=conversation_id, metadata_dict=metadata)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_messages(request, conversation_id):
    try:
        messages = registry.get_messages(conversation_id=conversation_id)
        return JsonResponse({"messages": [message.model_dump_json() for message in messages]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_metadata(request, conversation_id):
    try:
        metadata = registry.get_metadata(conversation_id=conversation_id)
        return JsonResponse({"metadata": metadata.model_dump_json()})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_users(request, conversation_id):
    try:
        users = registry.get_users(conversation_id=conversation_id)
        return JsonResponse({"users": [user.model_dump_json() for user in users]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def list_conversations(request):
    try:
        conversations = registry.get_conversations()
        # conversations is expected to be a dict or iterable of {id: metadata}
        result = [{"conversation_id": cid, "metadata": meta.model_dump_json()} for cid, meta in conversations.items()]
        return JsonResponse({"conversations": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
