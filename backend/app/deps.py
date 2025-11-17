import os
from pymongo import MongoClient
from .logger import logger

_client = None

def get_db():
    global _client
    if _client is None:
        try:
            logger.info("Conectando a la base de datos MongoDB")
            uri = os.getenv("MONGO_URI") or os.getenv("MONGO_URL") \
                or "mongodb://admin_user:web3@mongo:27017/?authSource=admin"
            _client = MongoClient(uri)
            _client.admin.command('ping')
            logger.info("Conexión a MongoDB establecida correctamente")
        except Exception as e:
            logger.error(f"Error al conectar con MongoDB: {str(e)}")
            raise
    return _client["calcdb"]

def reset_db_client():
    """Función para resetear el cliente (usado en tests)"""
    global _client
    _client = None