from .utils import validate_numbers, compute
from .repository import HistoryRepository
from .logger import logger

def perform_and_store(repo: HistoryRepository, op: str, numbers: list[float]) -> dict:
    try:
        logger.info(f"Ejecutando la operación '{op}' con numeros: {numbers}")
        validate_numbers(op, numbers)
        result = compute(op, numbers)
        _id = repo.insert(op, numbers, result)
        logger.info(f"Resultado de la operación '{op}': {result} almacenado con id: {_id}")
        return {"id": _id, "op": op, "numbers": numbers, "result": result}
    except Exception as e:
        logger.error(f"Error al ejecutar operación '{op}', números: {numbers}, error: {str(e)}")
        raise