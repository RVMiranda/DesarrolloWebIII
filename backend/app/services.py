from .utils import validate_numbers, compute
from .repository import HistoryRepository

def perform_and_store(repo: HistoryRepository, op: str, numbers: list[float]) -> dict:
    validate_numbers(op, numbers)
    result = compute(op, numbers)
    _id = repo.insert(op, numbers, result)
    return {"id": _id, "op": op, "numbers": numbers, "result": result}
