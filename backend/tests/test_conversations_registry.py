import json
import os
import shutil
import tempfile
from datetime import datetime
from os.path import join as pjoin

import pytest

from bourracho.conversations_registry import ConversationsRegistry
from bourracho.models import ConversationMetadata, Message, React, User

conv_ids = ["c1", "c2", "c3"]
users = [
    User(id="u1", name="Alice", pseudo="Eulyce", is_admin=True),
    User(id="u2", name="Bob"),
    User(id="u3", name="Alice"),
]


@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture
def sample_users():
    return [
        User(id="u1", name="Alice", pseudo="Eulyce", is_admin=True),
        User(id="u2", name="Bob"),
        User(id="u3", name="Alice"),
    ]


@pytest.fixture
def sample_metadata():
    return ConversationMetadata(id="c1", name="Test Conversation")


@pytest.fixture
def sample_message(sample_users):
    return Message(id="m1", content="Hello", timestamp=datetime.now(), issuer_id=sample_users[0].id)


def test_registry_init(temp_dir):
    conv_reg = ConversationsRegistry(conversations_registry_id="id1", persistence_dir=temp_dir)
    assert conv_reg.conversation_stores == {}
    assert conv_reg.persistence_dir == pjoin(temp_dir, "registry_id=id1")


def test_add_conversation_and_serialize(temp_dir, sample_metadata):
    conv_reg = ConversationsRegistry("reg1", temp_dir)
    conv_reg.add_conversation(sample_metadata)
    assert sample_metadata.id in conv_reg.conversation_stores
    # Check registry file exists
    assert os.path.exists(conv_reg.conversations_registry_filepath)
    # Check serialization does not raise
    conv_reg.serialize()


def test_get_all_conversations(temp_dir, sample_metadata):
    conv_reg = ConversationsRegistry("reg2", temp_dir)
    conv_reg.add_conversation(sample_metadata)
    all_convs = conv_reg.get_all_conversations()
    assert isinstance(all_convs, dict)
    assert sample_metadata.id in all_convs


def test_add_message_and_get_messages(temp_dir, sample_metadata, sample_message):
    conv_reg = ConversationsRegistry("reg3", temp_dir)
    conv_reg.add_conversation(sample_metadata)
    conv_reg.add_message(sample_message, sample_metadata.id)
    msgs = conv_reg.get_messages(sample_metadata.id)
    assert any(m.id == sample_message.id for m in msgs)


def test_add_user(temp_dir, sample_metadata, sample_users):
    conv_reg = ConversationsRegistry("reg4", temp_dir)
    conv_reg.add_conversation(sample_metadata)
    conv_reg.add_user_id_to_conversation(sample_users[1].id, sample_metadata.id)
    # No exception means success; further checks would require reading the store directly


def test_update_metadata(temp_dir, sample_metadata):
    conv_reg = ConversationsRegistry("reg5", temp_dir)
    conv_reg.add_conversation(sample_metadata)
    new_name = "Updated Name"
    conv_reg.update_metadata(sample_metadata.id, {"name": new_name})
    # No exception means success; further checks would require reading the store directly


def test_errors_on_invalid_conversation(temp_dir, sample_message, sample_users):
    conv_reg = ConversationsRegistry("reg6", temp_dir)
    with pytest.raises(ValueError):
        conv_reg.add_message(sample_message, "bad_id")
    with pytest.raises(ValueError):
        conv_reg.add_user_id_to_conversation(sample_users[0].id, "bad_id")
    with pytest.raises(ValueError):
        conv_reg.get_messages("bad_id")
    with pytest.raises(ValueError):
        conv_reg.update_metadata("bad_id", {"foo": "bar"})


def test_serialization(temp_dir, sample_metadata):
    conv_reg = ConversationsRegistry("reg7", temp_dir)
    conv_reg.add_conversation(sample_metadata)
    conv_reg.register_user(User(id="user1", name="Alice", pseudo="Eulyce", is_admin=True))
    conv_reg.add_message(
        Message(content="Hello", issuer_id="user1", id="m1", timestamp=datetime.now(), reacts=[]), sample_metadata.id
    )
    conv_reg.add_react(
        React(emoji="👍", issuer_id="user1"), conversation_id=sample_metadata.id, message_id="m1", user_id="user1"
    )
    conv_reg.serialize()
    assert os.path.exists(conv_reg.conversations_registry_filepath)
    with open(conv_reg.conversations_registry_filepath, "r") as f:
        d = json.load(f)
    d["users"]["user1"] = json.loads(d["users"]["user1"])
    assert d["id"] == "reg7"
    assert d["users"]["user1"]["id"] == "user1"
    assert d["users"]["user1"]["name"] == "Alice"
    assert d["users"]["user1"]["pseudo"] == "Eulyce"
    assert "db_dir" in d["conversation_stores"][sample_metadata.id]
    assert "conversation_id" in d["conversation_stores"][sample_metadata.id]
