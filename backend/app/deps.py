import os
from pymongo import MongoClient

_client = None

def get_db():
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI") or os.getenv("MONGO_URL") \
            or "mongodb://admin_user:web3@mongo:27017/?authSource=admin"
        _client = MongoClient(uri)
    return _client["calcdb"]

def reset_db_client():
    """Función para resetear el cliente (usado en tests)"""
    global _client
    _client = None