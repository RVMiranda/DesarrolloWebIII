from typing import List
from .errors import err_negatives, err_div_zero

def validate_numbers(op: str, numbers: List[float]):
    if any(x < 0 for x in numbers):
        err_negatives(op, numbers)
    if op == "div" and 0 in numbers[1:]:
        err_div_zero(op, numbers)

def compute(op: str, numbers: List[float]) -> float:
    if op == "sum":
        s = 0.0
        for n in numbers: s += n
        return s
    if op == "sub":
        acc = numbers[0]
        for n in numbers[1:]: acc -= n
        return acc
    if op == "mul":
        acc = 1.0
        for n in numbers: acc *= n
        return acc
    if op == "div":
        acc = numbers[0]
        for n in numbers[1:]:
            if n == 0:
                from .errors import err_div_zero
                err_div_zero("div", numbers)
            acc /= n
        return acc
    raise ValueError("op inválida")
