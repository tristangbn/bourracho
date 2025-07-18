from loguru import logger
from pymongo import MongoClient

from bourracho import config


def check_db_connection():
    try:
        client = MongoClient(config.MONGO_DB_URL)
        client.server_info()
        logger.success("Connection to Mongo DB OK.")
    except Exception as e:
        raise ValueError(f"Failed to connect to MongoDB: {e}") from e
