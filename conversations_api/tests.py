import json

from django.test import Client, TestCase


class ConversationsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.base_url = "/api/conversations/"

    def test_create_conversation(self):
        resp = self.client.post(
            self.base_url, data=json.dumps({"metadata": {"title": "Test"}}), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("conversation_id", resp.json())
        self.conversation_id = resp.json()["conversation_id"]

    def test_full_conversation_flow(self):
        # Create conversation
        resp = self.client.post(
            self.base_url, data=json.dumps({"metadata": {"title": "TestMeta"}}), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        conversation_id = resp.json()["conversation_id"]

        # Post message
        message_url = f"{self.base_url}{conversation_id}/messages/"
        msg = {"message": "Hello world!"}
        resp = self.client.post(message_url, data=json.dumps(msg), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")

        # Post metadata
        metadata_url = f"{self.base_url}{conversation_id}/metadata/"
        meta = {"metadata": {"author": "User1"}}
        resp = self.client.post(metadata_url, data=json.dumps(meta), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "success")

        # Get messages
        get_messages_url = f"{self.base_url}{conversation_id}/messages/get/"
        resp = self.client.get(get_messages_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("messages", resp.json())
        self.assertTrue(isinstance(resp.json()["messages"], list))
        self.assertIn("Hello world!", json.dumps(resp.json()["messages"]))

        # Get metadata
        get_metadata_url = f"{self.base_url}{conversation_id}/metadata/get/"
        resp = self.client.get(get_metadata_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("metadata", resp.json())
        self.assertIn("author", json.dumps(resp.json()["metadata"]))
