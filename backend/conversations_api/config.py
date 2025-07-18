import os

MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "bourracho_api_db2")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb://localhost:27017")
