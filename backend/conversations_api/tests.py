import json
import os
import shutil

from django.test import Client, TestCase

from conversations_api import config

config.REGISTRY_PERSISTENCE_DIR = "tmp/registry_persistence_dir/"
config.REGISTRY_ID = "test_registry"
if os.path.isdir(config.REGISTRY_PERSISTENCE_DIR):
    shutil.rmtree(config.REGISTRY_PERSISTENCE_DIR)


class ConversationsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_prefix = "/api/"

    def test_create_conversation(self):
        # Register user
        user_test = {"id": "user_test_2", "name": "Test User", "is_admin": True}
        resp = self.client.post(f"{self.api_prefix}auth/", data=json.dumps(user_test), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        # Create conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_test['id']}/create",
            data=json.dumps({"metadata": {"name": "Test"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("conversation_id", resp.json())
        self.conversation_id = resp.json()["conversation_id"]

    def test_full_conversation_flow(self):
        user_1 = {"id": "user_test_1", "name": "Test User", "is_admin": True}
        user_2 = {"id": "user_test_2", "name": "Alice", "pseudo": "AA", "is_admin": False}
        # Register user
        resp = self.client.post(f"{self.api_prefix}auth/", data=json.dumps(user_1), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        # Create conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_1['id']}/create",
            data=json.dumps({"metadata": {"name": "TestMeta"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        conversation_id = resp.json()["conversation_id"]
        # Join conversation (should be idempotent)
        join_url = f"{self.api_prefix}conversations/{user_2['id']}/join"
        resp = self.client.post(
            join_url, data=json.dumps({"conversation_id": conversation_id}), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        # Post message
        message_url = f"{self.api_prefix}messages/{user_2['id']}/{conversation_id}"
        msg = {"message": {"content": "Hello world!"}}
        resp = self.client.post(message_url, data=json.dumps(msg), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")
        # Post metadata
        metadata_url = f"{self.api_prefix}metadata/{user_2['id']}/{conversation_id}"
        meta = {"metadata": {"author": "User1"}}
        resp = self.client.post(metadata_url, data=json.dumps(meta), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        # Get messages
        get_messages_url = f"{self.api_prefix}messages/{user_2['id']}/{conversation_id}/get"
        resp = self.client.get(get_messages_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("messages", resp.json())
        self.assertTrue(isinstance(resp.json()["messages"], list))
        self.assertIn("Hello world!", json.dumps(resp.json()["messages"]))
        # Get metadata
        get_metadata_url = f"{self.api_prefix}metadata/{user_2['id']}/{conversation_id}/get"
        resp = self.client.get(get_metadata_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("metadata", resp.json())
        # List conversations for user
        list_url = f"{self.api_prefix}conversations/{user_2['id']}/get"
        resp = self.client.get(list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("conversations", resp.json())
        resp = resp.json()["conversations"]
        self.assertTrue(len(resp) == 2)
        self.assertTrue(any("TestMeta" in json.loads(c)["name"] for c in resp))
        # React to message
        react_url = f"{self.api_prefix}react/{user_2['id']}/{conversation_id}"
        messages = self.client.get(get_messages_url)
        react = {
            "react": {"emoji": "👍", "issuer_id": user_2["id"]},
            "message_id": json.loads(messages.json()["messages"][0])["id"],
        }
        resp = self.client.post(react_url, data=json.dumps(react), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        messages = self.client.get(get_messages_url)
        self.assertEqual(messages.status_code, 200)
        self.assertIn("messages", messages.json())
        self.assertTrue(isinstance(messages.json()["messages"], list))
        self.assertIn(str("👍".encode("utf-8")), json.dumps(messages.json()["messages"]))
