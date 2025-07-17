import json
import os
import shutil
import uuid

from django.test import Client, TestCase

from conversations_api import config


class ConversationsApiTests(TestCase):
    def setUp(self):
        if os.path.exists(config.REGISTRY_PERSISTENCE_DIR):
            shutil.rmtree(config.REGISTRY_PERSISTENCE_DIR)
        os.makedirs(config.REGISTRY_PERSISTENCE_DIR)

        self.client = Client()
        self.api_prefix = "/api/"
        self.userid_1 = str(uuid.uuid4())
        self.userid_2 = str(uuid.uuid4())

    def test_create_conversation(self):
        # Register user
        user_test = {"id": self.userid_1, "name": "Test User", "is_admin": True}
        resp = self.client.post(f"{self.api_prefix}auth/", data=json.dumps(user_test), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        # Create conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_test['id']}/create",
            data=json.dumps({"name": "Test"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("conversation_id", resp.json())
        self.assertTrue("conversation_id" in resp.json())
        conversation_id = resp.json()["conversation_id"]
        self.assertTrue(len(conversation_id) == 6)

    def test_join_conversation(self):
        user_test_1 = {"id": self.userid_1, "name": "Test User", "is_admin": True}
        user_test_2 = {"id": self.userid_2, "name": "Another User", "is_admin": False}
        resp = self.client.post(
            f"{self.api_prefix}auth/", data=json.dumps(user_test_1), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        # Create conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_test_1['id']}/create",
            data=json.dumps({"name": "Test"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("conversation_id", resp.json())
        self.conversation_id = resp.json()["conversation_id"]
        # Join conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_test_2['id']}/join",
            query_params={"conversation_id": self.conversation_id},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("status", resp.json())
        self.assertEqual(resp.json()["status"], "success")
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_test_1['id']}/join",
            query_params={"conversation_id": self.conversation_id},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("status", resp.json())
        self.assertEqual(resp.json()["status"], "success")

    def test_post_message(self):
        user_test_1 = {"id": self.userid_1, "name": "Test User", "is_admin": True}
        resp = self.client.post(
            f"{self.api_prefix}auth/", data=json.dumps(user_test_1), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        # Create conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_test_1['id']}/create",
            data=json.dumps({"name": "Test"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("conversation_id", resp.json())
        self.conversation_id = resp.json()["conversation_id"]
        # Post message
        message_url = f"{self.api_prefix}messages/{user_test_1['id']}/{self.conversation_id}"
        msg = {"content": "Hello world!"}
        resp = self.client.post(
            message_url,
            json.dumps(msg),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")

    def test_full_conversation_flow(self):
        user_1 = {"id": self.userid_1, "name": "Test User", "is_admin": True}
        user_2 = {"id": self.userid_2, "name": "Alice", "pseudo": "AA", "is_admin": False}
        # Register user
        resp = self.client.post(f"{self.api_prefix}auth/", data=json.dumps(user_1), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        # Create conversation
        resp = self.client.post(
            f"{self.api_prefix}conversations/{user_1['id']}/create",
            data=json.dumps({"name": "TestMeta"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        conversation_id = resp.json()["conversation_id"]
        # Join conversation (should be idempotent)
        join_url = f"{self.api_prefix}conversations/{user_2['id']}/join"
        resp = self.client.post(
            join_url, query_params={"conversation_id": conversation_id}, content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        # Post message
        message_url = f"{self.api_prefix}messages/{user_2['id']}/{conversation_id}"
        msg = {"content": "Hello world!"}
        resp = self.client.post(
            message_url,
            json.dumps(msg),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")
        # Post metadata
        metadata_url = f"{self.api_prefix}metadata/{user_2['id']}/{conversation_id}"
        meta = {"name": "conv name"}
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
        self.assertTrue(len(resp) == 1)
        self.assertTrue("conv name" in json.loads(resp[0])["name"])
        # React to message
        react_url = f"{self.api_prefix}react/{user_2['id']}/{conversation_id}"
        messages = self.client.get(get_messages_url)
        message_id = json.loads(messages.json()["messages"][0])["id"]
        resp = self.client.post(
            react_url,
            data=json.dumps({"emoji": "👍"}),
            content_type="application/json",
            query_params={"message_id": message_id},
        )
        self.assertEqual(resp.status_code, 200)
        messages = self.client.get(get_messages_url)
        self.assertEqual(messages.status_code, 200)
        self.assertIn("messages", messages.json())
        self.assertTrue(isinstance(messages.json()["messages"], list))
