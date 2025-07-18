import os
from pathlib import Path

BOURRACHO_ROOT_DIR = Path(__file__).parent.parent

PERSISTENCE_DIR = BOURRACHO_ROOT_DIR / "persistence"
MONGO_DB_URL = os.environ.get("MONGO_DB_URL", "mongodb://localhost:27017")
MONGO_DB_USERNAME = os.environ.get("MONGO_DB_USERNAME", None)
MONGO_DB_PASSWORD = os.environ.get("MONGO_DB_PASSWORD", None)
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "bourracho_db_dev")

CONVERSATIONS_COLLECTION = "conversations"
USERS_COLLECTION = "users"
MESSAGES_COLLECTION = "messages"
