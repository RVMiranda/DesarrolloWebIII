import logging
import sys
from datetime import datetime
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

def get_logger(name: str = "calculadora") -> logging.Logger:
    """
    Configura (si hace falta) y devuelve el logger principal de la app.

    - Envía logs a Loki con LokiLoggerHandler.
    - Además saca los logs por consola (docker logs).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si se llama varias veces
    has_loki = any(isinstance(h, LokiLoggerHandler) for h in logger.handlers)
    has_stream = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    if not has_loki:
        loki_handler = LokiLoggerHandler(
            url="http://loki:3100/loki/api/v1/push",
            # 👇 AQUÍ VAN LAS LABELS QUE VERÁS EN LOKI
            labels={"application": name},
            timeout=10,
        )
        logger.addHandler(loki_handler)

    if not has_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


# Logger global para usar en el resto de la app
logger = get_logger()