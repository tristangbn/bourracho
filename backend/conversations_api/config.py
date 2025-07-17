import os

REGISTRY_PERSISTENCE_DIR = os.environ.get("REGISTRY_PERSISTENCE_DIR", "registry_persistence_dir")
REGISTRY_ID = os.environ.get("REGISTRY_ID", "default_registry")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb://localhost:27017")
CONVERSATION_STORE_MODEL = {"type": "mongo_db", "db_uri": MONGO_DB_URI, "id": "default_id"}
