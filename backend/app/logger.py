import logging
import sys
from datetime import datetime

def setup_logger():
    logger = logging.getLogger("calculadora")
    logger.setLevel(logging.INFO)
    
    # Handler para stdout (Docker logs)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Formato detallado para los logs
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

logger = setup_logger()