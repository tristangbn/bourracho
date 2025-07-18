from unittest.mock import MagicMock, patch

import pytest

from bourracho.messages_store import MessagesStore
from bourracho.models import Message, React

MONGO_TEST_DB = "bourracho_test"


@pytest.fixture
def store() -> MessagesStore:
    with patch("bourracho.messages_store.MongoClient"):
        instance = MessagesStore(MONGO_TEST_DB)
        yield instance


def test_add_message_validates_and_inserts(store):
    message = MagicMock(spec=Message)
    message.model_dump.return_value = {"foo": "bar"}
    with (
        patch.object(store, "messages_collection") as mock_coll,
        patch("bourracho.messages_store.Message.model_validate") as mock_validate,
    ):
        store.add_message(message)
        mock_validate.assert_called_once_with(message)
        mock_coll.insert_one.assert_called_once_with(message.model_dump())


def test_get_messages_returns_validated(store):
    fake_msg = {"conversation_id": "cid", "id": "mid"}
    with (
        patch.object(store, "messages_collection") as mock_coll,
        patch("bourracho.messages_store.Message.model_validate", side_effect=lambda x: x),
    ):
        mock_coll.find.return_value = [fake_msg]
        result = store.get_messages("cid")
        assert result == [fake_msg]
        mock_coll.find.assert_called_once_with({"conversation_id": "cid"})


def test_add_react_success(store: MessagesStore):
    react = MagicMock(spec=React)
    react.model_dump.return_value = {"foo": "bar"}
    with patch.object(store, "messages_collection") as mock_coll:
        mock_coll.update_one.return_value.matched_count = 1
        with patch("bourracho.messages_store.logger") as mock_logger:
            store.add_react(react, "mid")
            mock_coll.update_one.assert_called_once_with({"id": "mid"}, {"$set": {"reacts": [react.model_dump()]}})
            mock_logger.info.assert_called()


def test_get_reacts(store: MessagesStore):
    fake_msg = {"id": "mid", "reacts": [{"foo": "bar"}]}
    with (
        patch.object(store, "messages_collection") as mock_coll,
        patch("bourracho.messages_store.React.model_validate", side_effect=lambda x: x),
    ):
        mock_coll.find_one.return_value = fake_msg
        result = store.get_reacts("mid")
        assert result == [{"foo": "bar"}]
        mock_coll.find_one.assert_called_once_with({"id": "mid"})
