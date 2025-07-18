from unittest.mock import MagicMock, patch

import pytest

from bourracho.conversations_store import ConversationsStore
from bourracho.models import Conversation

MONGO_TEST_DB = "bourracho_test"


@pytest.fixture
def store():
    with patch("bourracho.conversations_store.MongoClient"):
        instance = ConversationsStore(db_name=MONGO_TEST_DB)
        yield instance


def test_create_conversation_validates_and_inserts(store):
    conversation = MagicMock(spec=Conversation)
    conversation.model_dump.return_value = {"foo": "bar"}
    with (
        patch.object(store, "conversations_collection") as mock_coll,
        patch("bourracho.conversations_store.Conversation.model_validate") as mock_validate,
    ):
        store.add_conversation(conversation)
        mock_validate.assert_called_once_with(conversation)
        mock_coll.insert_one.assert_called_once_with(conversation.model_dump())


def test_get_conversation_returns_validated(store):
    fake_conv = {"id": "cid"}
    with (
        patch.object(store, "conversations_collection") as mock_coll,
        patch("bourracho.conversations_store.Conversation.model_validate", side_effect=lambda x: x),
    ):
        mock_coll.find_one.return_value = fake_conv
        result = store.get_conversation("cid")
        assert result == fake_conv
        mock_coll.find_one.assert_called_once_with({"id": "cid"})


def test_get_conversations_returns_list(store):
    fake_convs = [{"id": "cid", "users_ids": ["uid"]}]
    with (
        patch.object(store, "conversations_collection") as mock_coll,
        patch("bourracho.conversations_store.Conversation.model_validate", side_effect=lambda x: x),
    ):
        mock_coll.find.return_value = fake_convs
        result = store.get_conversations("uid")
        assert result == fake_convs
        mock_coll.find.assert_called_once_with({"users_ids": {"$in": ["uid"]}})


def test_add_user_id_to_conversation(store):
    with patch.object(store, "conversations_collection") as mock_coll:
        store.add_user_id_to_conversation("uid", "cid")
        mock_coll.update_one.assert_called_once_with({"id": "cid"}, {"$addToSet": {"users_ids": "uid"}})
