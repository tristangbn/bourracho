import json

import django
from django.test import Client, TestCase


class ConversationsApiTests(TestCase):
    def setUp(self):
        self.client: django.test.Client = Client()
        self.api_prefix = "/api/"

    def test_register_and_login(self):
        payload = {"username": "alice", "password": "secret123"}
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user = resp.json()
        self.assertTrue(user)

        # Try login
        resp = self.client.post(f"{self.api_prefix}login/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("username", resp.json())
        self.assertEqual(resp.json()["username"], "alice")

        # Get users
        resp = self.client.get(f"{self.api_prefix}users", query_params={"users_ids": [user["id"]]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]["username"], "alice")

    def test_create_conversation(self):
        # Register user
        payload = {"username": "bob", "password": "secret456"}
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user = resp.json()
        self.assertTrue(user)
        user_id = user["id"]
        # Create conversation (minimal required fields)
        conversation = {"name": "Test"}
        resp = self.client.post(
            f"{self.api_prefix}chat/",
            data=json.dumps(conversation),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("id", resp.json())
        conversation_id = resp.json()["id"]
        self.assertTrue(conversation_id)

    def test_join_conversation(self):
        # Register two users
        payload1 = {"username": "user1", "password": "pw1"}
        payload2 = {"username": "user2", "password": "pw2"}
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload1), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user_id1 = resp.json()["id"]
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload2), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user_id2 = resp.json()["id"]
        # Create conversation with user1
        conversation = {"name": "TestJoin", "is_locked": False}
        resp = self.client.post(
            f"{self.api_prefix}chat/",
            data=json.dumps(conversation),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id1},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["users_ids"], [user_id1])
        conversation_id = resp.json()["id"]
        # Join conversation with user2
        resp = self.client.post(
            f"{self.api_prefix}chat/{conversation_id}/join",
            content_type="application/json",
            **{"HTTP_USER_ID": user_id2},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("users_ids", resp.json())
        self.assertEqual(resp.json()["users_ids"], [user_id1, user_id2])
        # Join again with user1 (idempotent)
        resp = self.client.post(
            f"{self.api_prefix}chat/{conversation_id}/join",
            content_type="application/json",
            **{"HTTP_USER_ID": user_id1},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("users_ids", resp.json())
        self.assertCountEqual(resp.json()["users_ids"], [user_id1, user_id2])

        resp = self.client.get(
            f"{self.api_prefix}users",
            query_params={"users_ids": [user_id1, user_id2]},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)
        self.assertEqual(resp.json()[0]["username"], "user1")
        self.assertEqual(resp.json()[0]["id"], user_id1)
        self.assertEqual(resp.json()[1]["username"], "user2")
        self.assertEqual(resp.json()[1]["id"], user_id2)

    def test_post_message(self):
        # Register user
        payload = {"username": "msguser", "password": "pwmsg"}
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user_id = resp.json()["id"]
        # Create conversation
        conversation = {"name": "MsgTest", "is_locked": False}
        resp = self.client.post(
            f"{self.api_prefix}chat/",
            data=json.dumps(conversation),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id},
        )
        self.assertEqual(resp.status_code, 200)
        conversation_id = resp.json()["id"]
        # Post message
        msg = {"content": "Hello world!", "issuer_id": user_id, "conversation_id": conversation_id}
        resp = self.client.post(
            f"{self.api_prefix}chat/{conversation_id}/messages/",
            json.dumps(msg),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "Hello world!")

    def test_full_conversation_flow(self):
        # Register two users
        payload1 = {"username": "flowuser1", "password": "pwflow1"}
        payload2 = {"username": "flowuser2", "password": "pwflow2"}
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload1), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user_id1 = resp.json()["id"]
        resp = self.client.post(
            f"{self.api_prefix}register/", data=json.dumps(payload2), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        user_id2 = resp.json()["id"]
        # Create conversation with user1
        conversation = {"name": "TestMeta", "is_locked": False}
        resp = self.client.post(
            f"{self.api_prefix}chat/",
            data=json.dumps(conversation),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id1},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["users_ids"], [user_id1])
        conversation_id = resp.json()["id"]

        # Get users
        resp = self.client.get(
            f"{self.api_prefix}users",
            query_params={"users_ids": [user_id1]},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]["username"], "flowuser1")
        # Join conversation (should be idempotent)
        join_url = f"{self.api_prefix}chat/{conversation_id}/join"
        resp = self.client.post(join_url, content_type="application/json", **{"HTTP_USER_ID": user_id2})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["users_ids"], [user_id1, user_id2])
        # Post message

        msg = {"content": "Hello world!", "conversation_id": conversation_id, "issuer_id": user_id2}
        resp = self.client.post(
            f"{self.api_prefix}chat/{conversation_id}/messages/",
            data=json.dumps(msg),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id2},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "Hello world!")
        # Update conversation

        meta = {"name": "conv name", "is_locked": False}
        resp = self.client.patch(
            f"{self.api_prefix}chat/{conversation_id}",
            data=json.dumps(meta),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id2},
        )
        self.assertEqual(resp.status_code, 200)
        # Get messages
        resp = self.client.get(f"{self.api_prefix}chat/{conversation_id}/messages/", **{"HTTP_USER_ID": user_id2})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.json(), list))
        self.assertIn("Hello world!", json.dumps(resp.json()))
        # Get conversation
        resp = self.client.get(f"{self.api_prefix}chat/{conversation_id}", **{"HTTP_USER_ID": user_id2})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("name", resp.json())
        self.assertEqual(resp.json()["name"], "conv name")
        # List conversations for user

        resp = self.client.get(f"{self.api_prefix}chat/", **{"HTTP_USER_ID": user_id2})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.json()) == 1)
        self.assertTrue("conv name" in resp.json()[0]["name"])
        # React to message
        patch_message_url = f"{self.api_prefix}chat/{conversation_id}"
        get_messages_url = f"{self.api_prefix}chat/{conversation_id}/messages/"
        messages = self.client.get(get_messages_url)
        message_id = messages.json()[0]["id"]
        resp = self.client.patch(
            patch_message_url,
            data=json.dumps({"id": message_id, "reacts": [{"emoji": "👍", "issuer_id": user_id2}]}),
            content_type="application/json",
            **{"HTTP_USER_ID": user_id2},
        )
        self.assertEqual(resp.status_code, 200)
        messages = self.client.get(get_messages_url)
        self.assertEqual(messages.status_code, 200)
        self.assertTrue(isinstance(messages.json(), list))
