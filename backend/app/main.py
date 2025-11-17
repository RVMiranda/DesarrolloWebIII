from fastapi import FastAPI, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schemas import NumbersBody, HistoryFilters, BatchBody
from .deps import get_db
from .repository import HistoryRepository
from .services import perform_and_store
from .logger import logger
import traceback

app = FastAPI(title="Calc API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def repo_dep(db=Depends(get_db)):
    return HistoryRepository(db["history"])

@app.post("/api/batch", tags=["batch"])
def batch(body: BatchBody, repo: HistoryRepository = Depends(repo_dep)):
    logger.info(f"Iniciando operación batch con {len(body.items)} operaciones")
    items_out = []
    any_error = False
    for idx, it in enumerate(body.items):
        try:
            result = perform_and_store(repo, it.op, it.numbers)
            items_out.append({"index": idx, "status": "ok", "data": result})
            logger.info(f"Batch [{idx}]: Operación '{it.op}' completada exitosamente - Números: {it.numbers}, Resultado: {result['result']}")
        except HTTPException as e:
            any_error = True
            items_out.append({
                "index": idx,
                "status": "error",
                "error": e.detail,
                "status_code": e.status_code
            })
            logger.error(f"Batch [{idx}]: Error en operación '{it.op}' - Números: {it.numbers}, Error: {e.detail}")
        except Exception as e:
            any_error = True
            items_out.append({
                "index": idx,
                "status": "error",
                "error": {"code":"UNEXPECTED","message":str(e)},
                "status_code": 500
            })
            logger.error(f"Batch [{idx}]: Error inesperado en operación '{it.op}' - Números: {it.numbers}, Error: {str(e)}\n{traceback.format_exc()}")
    http_code = getattr(status, "HTTP_207_MULTI_STATUS", 207)
    if not any_error:
        http_code = status.HTTP_200_OK
        logger.info("Operación batch completada sin errores - Total : {len(body.items)} operaciones exitosas")
    else:
        logger.warning(f"Operación batch completada con errores - Exitosas: {len([x for x in items_out if x['status']=='ok'])}, Fallidas: {len([x for x in items_out if x['status']=='error'])}")

    return JSONResponse(status_code=http_code, content={"items": items_out})


@app.post("/api/{op}", tags=["operations"])
def operation(op: str, body: NumbersBody, repo: HistoryRepository = Depends(repo_dep)):
    logger.info(f"Ejecutando operación '{op}' con números: {body.numbers}")
    if op not in {"sum","sub","mul","div"}:
        logger.error(f"Operación inválida: '{op}'")
        raise HTTPException(status_code=404, detail="operación inválida")
    try:
        result = perform_and_store(repo, op, body.numbers)
        logger.info(f"Operación '{op}' completada exitosamente - Números: {body.numbers}, Resultado: {result['result']}")
        return result
    except HTTPException as e:
        logger.error(f"Error en operación '{op}' - Números: {body.numbers}, Error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en operación '{op}' - Números: {body.numbers}, Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="error interno del servidor: " + str(e))

@app.get("/api/history", tags=["history"])
def history(filters: HistoryFilters = Depends(), repo: HistoryRepository = Depends(repo_dep)):
    try:
        logger.info(f"Obteniendo historial con filtros: op={filters.op}, date_from={filters.date_from}, date_to={filters.date_to}, sort_by={filters.sort_by}, order={filters.order}")
        items = repo.find(op=filters.op, date_from=filters.date_from, date_to=filters.date_to,
                    sort_by=filters.sort_by, order=filters.order)
        logger.info(f"Historial obtenido: {len(items)} registros encontrados")
        return {"items": items}
    except Exception as e:
        logger.error(f"Error inesperado al obtener historial - Filtros: op={filters.op}, date_from={filters.date_from}, date_to={filters.date_to}, sort_by={filters.sort_by}, order={filters.order}, Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="error interno del servidor: " + str(e))

@app.get("/health", tags=["health"])
def health():
    return {"ok": True}

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando la aplicación Calc API")
    logger.info("Backend de Calculadora iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Apagando la aplicación Calc API")
    logger.info("Backend de Calculadora apagada correctamente")