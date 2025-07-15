from django.urls import path

from . import views

urlpatterns = [
    path("auth/", views.register_user, name="register_user"),
    path("conversations/<str:user_id>/create", views.create_conversation, name="create_conversation"),
    path("conversations/<str:user_id>/get", views.list_conversations, name="list_conversations"),
    path("conversations/<str:user_id>/join", views.join_conversation, name="join_conversation"),
    path("users/<str:user_id>/<str:conversation_id>/get", views.get_users, name="get_users"),
    path("messages/<str:user_id>/<str:conversation_id>", views.post_message, name="post_message"),
    path("messages/<str:user_id>/<str:conversation_id>/get", views.get_messages, name="get_messages"),
    path("metadata/<str:user_id>/<str:conversation_id>", views.post_metadata, name="post_metadata"),
    path("metadata/<str:user_id>/<str:conversation_id>/get", views.get_metadata, name="get_metadata"),
    path("react/<str:user_id>/<str:conversation_id>", views.post_react, name="post_react"),
]
