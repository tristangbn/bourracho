from django.urls import path

from . import views

urlpatterns = [
    path("conversations/", views.create_conversation, name="create_conversation"),
    path("conversations/<str:conversation_id>/message/", views.post_message, name="post_message"),
    path("conversations/<str:conversation_id>/metadata/", views.post_metadata, name="post_metadata"),
    path("conversations/<str:conversation_id>/user/", views.post_user, name="post_user"),
    path("conversations/<str:conversation_id>/users/get/", views.get_users, name="get_users"),
    path("conversations/<str:conversation_id>/messages/get/", views.get_messages, name="get_messages"),
    path("conversations/<str:conversation_id>/metadata/get/", views.get_metadata, name="get_metadata"),
    path("conversations/all/", views.list_conversations, name="list_conversations"),
]
