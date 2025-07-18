import uuid

import bcrypt
from loguru import logger
from pymongo import MongoClient

from bourracho import config
from bourracho.models import User


class UsersStore:
    def __init__(self, db_name: str):
        self.db_name = db_name
        auth_kgws = {}
        if config.MONGO_DB_PASSWORD and config.MONGO_DB_USERNAME:
            auth_kgws = {"username": config.MONGO_DB_USERNAME, "password": config.MONGO_DB_PASSWORD}
        self.client = MongoClient(config.MONGO_DB_URL, **auth_kgws)
        self.db = self.client[self.db_name]
        self.users_collection = self.db[config.USERS_COLLECTION]

    def get_new_user(self, username: str, password: str) -> User:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(id=str(uuid.uuid4()), username=username, password_hash=password_hash)
        return user

    def check_credentials(self, username: str, password: str) -> str | None:
        if username not in self.users_collection.find_one({"username": username}):
            logger.info(f"No user found with username {username}")
            raise KeyError(f"User with username {username} not found")
        user = User.model_validate(self.users_collection.find_one({"username": username}))
        if not user:
            logger.info(f"No user found with username {username}")
            return None
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            logger.info(f"Password check failed for user {username}")
            return None
        return user.id

    def add_user(self, user: User) -> None:
        if user.username in self.users_collection.find_one({"username": user.username}):
            raise ValueError("User with username {} already exists".format(user.username))
        self.users_collection.insert_one(user.model_dump())

    def get_user(self, user_id: str) -> User | None:
        user = self.users_collection.find_one({"id": user_id})
        if not user:
            logger.info(f"No user found with id {user_id}")
            return None
        return User.model_validate(user)

    def get_users(self, user_ids: list[str]) -> list[User]:
        if user_ids == "*":
            users = self.users_collection.find()
        else:
            users = self.users_collection.find({"id": {"$in": user_ids}})
        return [User.model_validate(user) for user in users]
