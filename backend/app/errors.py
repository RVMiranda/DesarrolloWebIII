from fastapi import HTTPException, status

def err_negatives(op, numbers):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code":"NEGATIVOS_NO_PERMITIDOS","message":"No se aceptan los números negativos",
                "op": op, "numbers": numbers}
    )

def err_div_zero(op, numbers):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code":"DIVISION_CERO","message":"División entre cero no se puede realizar",
                "op": op, "numbers": numbers}
    )
