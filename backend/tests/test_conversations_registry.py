import json
import os
import uuid
from datetime import datetime
from itertools import product
from os.path import join as pjoin

import pytest
from pymongo import MongoClient

from bourracho.conversations_registry import ConversationsRegistry
from bourracho.models import (
    ConversationMetadata,
    JsonConversationStoreModel,
    Message,
    MongoConversationStoreModel,
    React,
    User,
)

conv_ids = ["c1", "c2", "c3"]
users = [
    User(id="u1", name="Alice", pseudo="Eulyce", is_admin=True),
    User(id="u2", name="Bob"),
    User(id="u3", name="Alice"),
]

client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
client.server_info()


@pytest.fixture
def sample_users():
    return [
        User(id="u1", name="Alice", pseudo="Eulyce", is_admin=True),
        User(id="u2", name="Bob"),
        User(id="u3", name="Alice"),
    ]


@pytest.fixture
def sample_conversation_metadata():
    return ConversationMetadata(id=str(uuid.uuid4()), name="Test Conversation")


@pytest.fixture
def sample_message(sample_users):
    return Message(id=str(uuid.uuid4()), content="Hello", timestamp=datetime.now(), issuer_id=sample_users[0].id)


def test_registry_init(tmpdir):
    reg = ConversationsRegistry(conversations_registry_id="id1", persistence_dir=tmpdir)
    assert reg.conversation_stores == {}
    assert reg.persistence_dir == pjoin(tmpdir, "registry_id=id1")


@pytest.mark.parametrize(
    "conversation_store_model,conversation_store_kwgs",
    [
        (JsonConversationStoreModel, {}),
        (MongoConversationStoreModel, {"db_uri": "mongodb://localhost:27017"}),
    ],
)
def test_add_conversation_and_serialize(
    sample_conversation_metadata, conversation_store_model, conversation_store_kwgs, tmpdir
):
    reg = ConversationsRegistry("reg1", tmpdir)
    conversation_store_kwgs["db_dir"] = str(tmpdir)
    reg.add_conversation(
        sample_conversation_metadata, conversation_store_model=conversation_store_model(**conversation_store_kwgs)
    )
    assert sample_conversation_metadata.id in reg.conversation_stores
    assert os.path.exists(reg.conversations_registry_filepath)
    reg.serialize()


@pytest.mark.parametrize(
    "testcase,conversation_store_model_and_kwgs",
    product(
        [
            "get_all_conversations",
            "add_message_and_get_messages",
            "add_user",
            "update_metadata",
            "errors_on_invalid_conversation",
            "serialization",
        ],
        [
            (JsonConversationStoreModel, {}),
            (MongoConversationStoreModel, {"db_uri": "mongodb://localhost:27017"}),
        ],
    ),
)
def test_registry_cases(
    testcase, tmpdir, sample_conversation_metadata, sample_message, sample_users, conversation_store_model_and_kwgs
):
    # Setup registry
    reg = ConversationsRegistry(f"reg_{testcase}", tmpdir)
    conversation_store_model, conversation_store_kwgs = conversation_store_model_and_kwgs
    conversation_store_kwgs["db_dir"] = str(tmpdir)
    conversation_store_model = conversation_store_model(**conversation_store_kwgs)

    if testcase == "list_conversations":
        reg.add_conversation(sample_conversation_metadata, conversation_store_model=conversation_store_model)
        all_convs = reg.list_conversations(user_id=sample_users[0].id)
        assert isinstance(all_convs, list)
        assert sample_conversation_metadata.id in all_convs

    elif testcase == "add_message_and_get_messages":
        reg.add_conversation(sample_conversation_metadata, conversation_store_model=conversation_store_model)
        reg.add_message(sample_message, sample_conversation_metadata.id)
        msgs = reg.get_messages(sample_conversation_metadata.id)
        assert any(m.id == sample_message.id for m in msgs)

    elif testcase == "add_user":
        reg.add_conversation(sample_conversation_metadata, conversation_store_model=conversation_store_model)
        reg.add_user_id_to_conversation(sample_users[1].id, sample_conversation_metadata.id)
        # No exception means success

    elif testcase == "update_metadata":
        reg.add_conversation(sample_conversation_metadata, conversation_store_model=conversation_store_model)
        new_name = "Updated Name"
        reg.update_metadata(sample_conversation_metadata.id, {"name": new_name})
        # No exception means success

    elif testcase == "errors_on_invalid_conversation":
        with pytest.raises(ValueError):
            reg.add_message(sample_message, "bad_id")
        with pytest.raises(ValueError):
            reg.add_user_id_to_conversation(sample_users[0].id, "bad_id")
        with pytest.raises(ValueError):
            reg.get_messages("bad_id")
        with pytest.raises(ValueError):
            reg.update_metadata("bad_id", {"foo": "bar"})

    elif testcase == "serialization":
        reg.add_conversation(sample_conversation_metadata, conversation_store_model=conversation_store_model)
        reg.register_user(User(id="user1", name="Alice", pseudo="Eulyce", is_admin=True))
        reg.add_message(
            Message(content="Hello", issuer_id="user1", id="m1", timestamp=datetime.now(), reacts=[]),
            sample_conversation_metadata.id,
        )
        reg.add_react(
            React(emoji="👍", issuer_id="user1"), conversation_id=sample_conversation_metadata.id, message_id="m1"
        )
        reg.serialize()
        assert os.path.exists(reg.conversations_registry_filepath)
        with open(reg.conversations_registry_filepath, "r") as f:
            d = json.load(f)
        d["users"]["user1"] = json.loads(d["users"]["user1"])
        assert d["id"] == f"reg_{testcase}"
        assert d["users"]["user1"]["id"] == "user1"
        assert d["users"]["user1"]["name"] == "Alice"
        assert d["users"]["user1"]["pseudo"] == "Eulyce"
        assert (
            "db_uri" in d["conversation_stores"][sample_conversation_metadata.id]
            or "db_dir" in d["conversation_stores"][sample_conversation_metadata.id]
        )
        assert "id" in d["conversation_stores"][sample_conversation_metadata.id]


@pytest.mark.parametrize(
    "conversation_store_model_and_kwgs",
    [
        (JsonConversationStoreModel, {}),
        (MongoConversationStoreModel, {"db_uri": "mongodb://localhost:27017"}),
    ],
)
def test_reload_registry(
    tmpdir, sample_conversation_metadata, sample_message, sample_users, conversation_store_model_and_kwgs
):
    conversation_store_model, conversation_store_kwgs = conversation_store_model_and_kwgs
    reg = ConversationsRegistry("reload_me", tmpdir)
    conversation_store_kwgs["db_dir"] = str(tmpdir)
    reg.register_user(sample_users[0])
    reg.create_conversation(
        user_id=sample_users[0].id,
        metadata=sample_conversation_metadata,
        conversation_store_model=conversation_store_model(**conversation_store_kwgs),
    )
    message = Message(content="Hello", issuer_id=sample_users[0].id, id="m1", timestamp=datetime.now(), reacts=[])
    reg.add_message(message, sample_conversation_metadata.id)
    reg.add_react(
        React(emoji="👍", issuer_id=sample_users[0].id),
        conversation_id=sample_conversation_metadata.id,
        message_id="m1",
    )
    reg.serialize()
    reg2 = ConversationsRegistry("reload_me", tmpdir)
    assert reg2.conversation_stores_models == reg.conversation_stores_models
    assert (
        reg2.list_conversations(user_id=sample_users[0].id)
        == reg.list_conversations(user_id=sample_users[0].id)
        == [sample_conversation_metadata]
    )
    assert (
        len(reg2.get_messages(conversation_id=sample_conversation_metadata.id))
        == len(reg.get_messages(conversation_id=sample_conversation_metadata.id))
        == 1
    )
    assert reg2.get_messages(conversation_id=sample_conversation_metadata.id) == reg.get_messages(
        conversation_id=sample_conversation_metadata.id
    )
    assert (
        reg2.get_users(conversation_id=sample_conversation_metadata.id)
        == reg.get_users(conversation_id=sample_conversation_metadata.id)
        == [sample_users[0].id]
    )
    assert reg2.get_user(user_id=sample_users[0].id) == reg.get_user(user_id=sample_users[0].id) == sample_users[0]
    assert (
        reg2.get_metadata(conversation_id=sample_conversation_metadata.id)
        == reg.get_metadata(conversation_id=sample_conversation_metadata.id)
        == sample_conversation_metadata
    )
