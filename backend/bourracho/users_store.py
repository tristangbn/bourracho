import uuid

import bcrypt
from loguru import logger
from pymongo import MongoClient

from bourracho import config
from bourracho.models import User


class UsersStore:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.client = MongoClient(config.MONGO_DB_URL)
        self.db = self.client[self.db_name]
        self.users_collection = self.db[config.USERS_COLLECTION]
        logger.info("Successfully initialized Users Store")

    @logger.catch
    def get_new_user(self, username: str, password: str) -> User:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(id=str(uuid.uuid4()), username=username, password_hash=password_hash)
        return user

    @logger.catch
    def check_credentials(self, username: str, password: str) -> str | None:
        db_user = self.users_collection.find_one({"username": username})
        if not db_user:
            logger.info(f"No user found with username {username}")
            return None
        user = User.model_validate(db_user)
        logger.info("User found with username {}".format(username))
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            logger.info(f"Password check failed for user {username}")
            return None
        return user.id

    @logger.catch
    def add_user(self, user: User) -> None:
        matching_usernames = self.users_collection.find_one({"username": user.username})
        if matching_usernames and user.username in matching_usernames:
            raise ValueError("User with username {} already exists".format(user.username))
        logger.info(f"Adding user with username {user.username} to collection.")
        self.users_collection.insert_one(user.model_dump())
        logger.info(f"User with username {user.username} added to collection.")

    @logger.catch
    def get_user(self, user_id: str) -> User | None:
        user = self.users_collection.find_one({"id": user_id})
        if not user:
            logger.info(f"No user found with id {user_id}")
            return None
        return User.model_validate(user)

    @logger.catch
    def get_users(self, user_ids: list[str]) -> list[User]:
        if user_ids == "*":
            users = self.users_collection.find()
        else:
            users = self.users_collection.find({"id": {"$in": user_ids}})
        return [User.model_validate(user) for user in users]
