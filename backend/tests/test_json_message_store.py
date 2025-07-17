import shutil
import tempfile
from datetime import datetime

import pytest

from bourracho.conversation_store.json_conversation_store import JsonConversationStore
from bourracho.models import ConversationMetadata, Message, React, User


@pytest.fixture
def temp_db_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture
def sample_user():
    return User(id="u1", name="Alice")


@pytest.fixture
def sample_message(sample_user):
    return Message(id="m1", content="Hello", timestamp=datetime.now(), issuer_id=sample_user.id)


@pytest.fixture
def sample_metadata():
    return ConversationMetadata(id="c1", name="Test Conversation")


def test_add_and_get_message(temp_db_dir, sample_message):
    store = JsonConversationStore(temp_db_dir, "c1")
    store.add_message(sample_message)
    store.add_react(React(emoji="👍", issuer_id="user1"), message_id="m1")
    messages = store.get_messages()
    assert len(messages) == 1
    assert messages[0].id == sample_message.id
    assert messages[0].content == sample_message.content
    assert messages[0].reacts == [React(emoji="👍", issuer_id="user1")]
    assert messages[0].issuer_id == sample_message.issuer_id


def test_get_messages_empty(temp_db_dir):
    store = JsonConversationStore(temp_db_dir, "c1")
    messages = store.get_messages()
    assert messages == []


def test_add_and_get_user(temp_db_dir, sample_user):
    store = JsonConversationStore(temp_db_dir, "c1")
    store.add_user_id(sample_user.id)
    users = store.get_users_ids()
    assert users == [sample_user.id]


def test_get_users_empty(temp_db_dir):
    store = JsonConversationStore(temp_db_dir, "c1")
    users = store.get_users_ids()
    assert users == []


def test_get_and_write_metadata(temp_db_dir, sample_metadata):
    store = JsonConversationStore(temp_db_dir, "c1")
    # Initially empty
    meta = store.get_metadata()
    assert isinstance(meta, ConversationMetadata)
    # Write and read
    store.write_metadata(sample_metadata)
    meta2 = store.get_metadata()
    assert meta2.id == sample_metadata.id
    assert meta2.name == sample_metadata.name


def test_update_metadata(temp_db_dir, sample_metadata):
    store = JsonConversationStore(temp_db_dir, "c1")
    store.write_metadata(sample_metadata)
    store.update_metadata({"name": "Updated Name"})
    meta = store.get_metadata()
    assert meta.name == "Updated Name"
