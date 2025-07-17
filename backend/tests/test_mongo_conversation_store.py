import random
import string

import emoji as emj
import pytest

from bourracho.conversation_store.mongo_conversation_store import MongoConversationStore
from bourracho.models import ConversationMetadata, Message, React

MONGO_TEST_URI = "mongodb://localhost:27017/"
MONGO_TEST_DB = "bourracho_test"


@pytest.fixture
def store():
    return MongoConversationStore(MONGO_TEST_URI, "".join(random.choices(string.ascii_letters, k=4)))


def test_write_and_get_messages(store):
    m1 = Message(content="Hello", issuer_id="u1", id="m1")
    m2 = Message(content="World", issuer_id="u2", id="m2")
    store.write_messages([m1, m2])
    messages = store.get_messages()
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].issuer_id == "u2"


def test_add_message(store):
    m = Message(content="Test", issuer_id="u3", id="m3")
    store.add_message(m)
    messages = store.get_messages()
    assert len(messages) == 1
    assert messages[0].content == "Test"


def test_users(store):
    store.add_user_id("user1")
    store.add_user_id("user2")
    users = store.get_users_ids()
    assert "user1" in users
    assert "user2" in users
    store.add_user_id("user1")  # duplicate, should not add again
    users = store.get_users_ids()
    assert users.count("user1") == 1


def test_metadata(store):
    meta = ConversationMetadata(name="test", id="metaid", is_locked=False)
    store.write_metadata(meta)
    fetched = store.get_metadata()
    assert fetched.name == "test"
    assert fetched.id == "metaid"
    assert fetched.is_locked is False

    store.update_metadata({"name": "updated"})
    fetched = store.get_metadata()
    assert fetched.name == "updated"


def test_add_react(store):
    m = Message(content="ReactMsg", issuer_id="u4", id="m5")
    store.add_message(m)
    react = React(emoji=":thumbs_up:", issuer_id="u4")
    store.add_react(react, message_id="m5")
    messages = store.get_messages()
    assert len(messages[0].reacts) == 1
    assert messages[0].reacts[0].emoji == emj.emojize(":thumbs_up:")
