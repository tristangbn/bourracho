import os
import random
import string

import pytest
from pymongo import MongoClient

from bourracho.models import Conversation, Message, React
from bourracho.stores_registry import StoresRegistry

MONGO_URL = os.environ.get("MONGO_DB_URL", "mongodb://localhost:27017/")


def random_db_name():
    return "test_bourracho_" + "".join(random.choices(string.ascii_lowercase, k=8))


def drop_database(db_name):
    client = MongoClient(MONGO_URL)
    client.drop_database(db_name)


@pytest.fixture(scope="function")
def stores_registry() -> StoresRegistry:
    db_name = random_db_name()
    store = StoresRegistry(db_name)
    yield store
    drop_database(db_name)


def test_auth(stores_registry: StoresRegistry):
    user = stores_registry.register_user(username="charlie", password="password")
    authed_user = stores_registry.check_credentials("charlie", "password")
    assert authed_user == user.id
    authed_user = stores_registry.check_credentials("charlie", "wrong_password")
    assert authed_user is None
    retrieved = stores_registry.get_user(user.id)
    assert retrieved.id == user.id
    assert retrieved.username == user.username


def test_conversations(stores_registry: StoresRegistry):
    user1 = stores_registry.register_user(username="charlie", password="password")
    user2 = stores_registry.register_user(username="alice", password="password")
    conv1 = Conversation(name="Test")
    conv2 = Conversation(name="Test")
    conv_id = stores_registry.create_conversation(user1.id, conv1)
    conv2_id = stores_registry.create_conversation(user1.id, conv2)
    conversations = stores_registry.list_conversations(user1.id)
    assert len(conversations) == 2
    assert any(c.id == conv_id for c in conversations)
    assert any(c.id == conv2_id for c in conversations)
    stores_registry.join_conversation(user2.id, conv_id)
    conversations = stores_registry.list_conversations(user2.id)
    assert len(conversations) == 1
    assert any(c.id == conv_id for c in conversations)
    conversations = stores_registry.list_conversations(user1.id)
    assert len(conversations) == 2
    assert any(c.id == conv_id for c in conversations)
    assert any(c.id == conv2_id for c in conversations)
    stores_registry.update_conversation(Conversation(id=conv_id, name="Test2", is_locked=True, random_key="x"))
    conversation = stores_registry.get_conversation(conv_id)
    assert conversation.id == conv_id
    assert conversation.name == "Test2"
    assert conversation.users_ids == [user1.id, user2.id]


def test_messages(stores_registry: StoresRegistry):
    user1 = stores_registry.register_user(username="charlie", password="password")
    user2 = stores_registry.register_user(username="alice", password="password")
    conv = Conversation(name="Test")
    conv2 = Conversation(name="Test2")
    # Create and join conversations
    conv1_id = stores_registry.create_conversation(user1.id, conv)
    conv2_id = stores_registry.create_conversation(user1.id, conv2)
    stores_registry.join_conversation(user1.id, conv1_id)
    stores_registry.join_conversation(user2.id, conv1_id)

    # User 1 post a first message to conv 1 and react to it
    stores_registry.add_message(Message(content="Hello !", conversation_id=conv1_id, issuer_id=user1.id))
    assert len(stores_registry.get_messages(conv1_id)) == 1
    assert stores_registry.get_messages(conv1_id)[0].content == "Hello !"
    stores_registry.add_react(React(emoji="👍", issuer_id=user1.id), stores_registry.get_messages(conv1_id)[0].id)
    assert stores_registry.get_messages(conv1_id)[0].content == "Hello !"
    assert stores_registry.get_messages(conv1_id)[0].reacts == [React(emoji="👍", issuer_id=user1.id)]

    # User 2 adds a message to conv 1
    stores_registry.add_message(Message(content="Hello back 🤩", conversation_id=conv1_id, issuer_id=user2.id))
    conv1_messages = stores_registry.get_messages(conv1_id)
    assert len(conv1_messages) == 2
    assert conv1_messages[0].content == "Hello !"
    assert conv1_messages[1].content == "Hello back 🤩"

    # User 1 overrides it react
    stores_registry.add_react(React(emoji="🤩", issuer_id=user1.id), conv1_messages[0].id)
    conv1_messages = stores_registry.get_messages(conv1_id)
    assert conv1_messages[0].reacts == [React(emoji="🤩", issuer_id=user1.id)]

    # User 1 adds a message to conv 2
    stores_registry.add_message(Message(content="Hello conv 2!", conversation_id=conv2_id, issuer_id=user1.id))
    conv2_messages = stores_registry.get_messages(conv2_id)
    assert len(conv2_messages) == 1
    assert conv2_messages[0].content == "Hello conv 2!"

    # User 2 reacts to conv 1
    stores_registry.add_react(React(emoji="👍", issuer_id=user2.id), conv1_messages[0].id)
    conv1_messages = stores_registry.get_messages(conv1_id)
    assert conv1_messages[0].reacts[0].emoji == "🤩"
    assert conv1_messages[0].reacts[1].emoji == "👍"
