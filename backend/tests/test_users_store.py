from unittest.mock import MagicMock, patch

import pytest

from bourracho.models import User
from bourracho.users_store import UsersStore

MONGO_TEST_DB = "bourracho_test"


@pytest.fixture
def store():
    with patch("bourracho.users_store.MongoClient"):
        instance = UsersStore(MONGO_TEST_DB)
        yield instance


def test_add_user_inserts(store):
    user = MagicMock(spec=User)
    user.model_dump.return_value = {"foo": "bar"}
    with patch.object(store, "users_collection") as mock_coll:
        store.add_user(user)
        mock_coll.insert_one.assert_called_once_with(user.model_dump())


def test_get_user_found(store):
    fake_user = {"id": "uid"}
    with (
        patch.object(store, "users_collection") as mock_coll,
        patch("bourracho.users_store.User.model_validate", side_effect=lambda x: x),
    ):
        mock_coll.find_one.return_value = fake_user
        result = store.get_user("uid")
        assert result == fake_user
        mock_coll.find_one.assert_called_once_with({"id": "uid"})


def test_get_user_not_found(store):
    with patch.object(store, "users_collection") as mock_coll:
        mock_coll.find_one.return_value = None
        result = store.get_user("uid")
        assert result is None
        mock_coll.find_one.assert_called_once_with({"id": "uid"})


def test_check_credentials(store):
    with patch.object(store, "users_collection") as mock_coll:
        user = store.get_new_user("uid", "pwd")
        store.add_user(user)
        mock_coll.find_one.return_value = user
        result = store.check_credentials("uid", "pwd")
        assert result == user.id
        mock_coll.find_one.assert_called_once_with({"username": "uid"})
