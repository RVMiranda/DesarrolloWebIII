from fastapi import FastAPI, Depends, status, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from .schemas import NumbersBody, HistoryFilters, BatchBody
from .deps import get_db
from .repository import HistoryRepository
from .services import perform_and_store
from .logger import logger
import traceback
import time
import os
import psutil
import datetime
import asyncio
from pydantic import BaseModel, field_validator
from typing import List
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = FastAPI(title="Calc API")

_process = psutil.Process(os.getpid())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_ok(operacion, datos, resultado):
    logger.info(f"[OK] {operacion} | Entrada={datos} | Resultado={resultado}")

def log_fail(operacion, datos, causa):
    logger.error(f"[ERROR] {operacion} | Motivo={causa} | Entrada={datos}")

def log_mongo_error(causa):
    logger.error(f"[MONGO ERROR] {causa}")

# * Metricas pra prometheus

operations_counter = Counter(
    'calculator_operations_total',
    'Total de operaciones realizadas',
    ['operation', 'status']  # labels: sum/sub/mul/div y success/error
)

# Histograma de duración de operaciones #! en segundos
operation_duration = Histogram(
    'calculator_operation_duration_seconds',
    'Duración de las operaciones en segundos',
    ['operation']
)

# Contador de errores por tipo
errors_counter = Counter(
    'calculator_errors_total',
    'Total de errores por tipo',
    ['error_type', 'operation']
)

# Contador de consultas al historial
history_queries = Counter(
    'calculator_history_queries_total',
    'Total de consultas al historial',
    ['status']
)

cpu_usage = Gauge('calculator_cpu_usage_percent', 'Uso de CPU del proceso en porcentaje')
memory_usage = Gauge('calculator_memory_usage_bytes', 'Uso de memoria del proceso en bytes')
memory_percent = Gauge('calculator_memory_usage_percent', 'Uso de memoria del proceso en porcentaje')

instrumentator = Instrumentator().instrument(app).expose(app)

def get_process():
    global _process
    if _process is None:
        _process = psutil.Process(os.getpid())
    return _process

def update_system_metrics():
    """
    Actualiza los gauges de CPU y memoria del proceso actual.
    """
    try:
        logger.info("Actualizando métricas de sistema")
        proc = _process
        # CPU:
        # - La primera llamada a cpu_percent() suele devolver 0.0
        # - Luego se basa en el delta desde la última llamada.
        # - Dividimos entre el número de CPUs para tener un % más real por proceso.
        cpu = proc.cpu_percent(interval=0.1)
        #cpu = cpu / psutil.cpu_count() if psutil.cpu_count() else cpu

        # Memoria:
        mem_info = proc.memory_info()  # bytes RSS del proceso
        mem_percent_value = proc.memory_percent()
        
        cpu_usage.set(cpu)
        memory_usage.set(mem_info.rss)
        memory_percent.set(mem_percent_value)
        logger.info(f"Métricas actualizadas: CPU={cpu}%, Memoria={mem_info.rss} bytes ({mem_percent_value}%)")
    except Exception as e:
        logger.error(f"Error actualizando métricas de sistema: {e}")

async def system_metrics_loop(interval_seconds: int = 5):
    """
    Loop asíncrono que actualiza las métricas de CPU/memoria cada N segundos.
    """
    logger.info("Iniciando loop de métricas de sistema (CPU/Memoria)")
    # Primera llamada para evitar que la métrica se quede mucho tiempo en 0.0
    update_system_metrics()

    while True:
        update_system_metrics()
        await asyncio.sleep(interval_seconds)


def repo_dep(db=Depends(get_db)):
    return HistoryRepository(db["history"])

# * ENDPPOINTS    

@app.get("/metrics", tags=["monitoring"])
def metrics():
    """Endpoint para que Prometheus scrape las métricas"""
    #* Actualizar métricas de sistema antes de devolver
    update_system_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/batch", tags=["batch"])
def batch(body: BatchBody, repo: HistoryRepository = Depends(repo_dep)):
    logger.info(f"Iniciando operación batch con {len(body.items)} operaciones")
    items_out = []
    any_error = False
    for idx, it in enumerate(body.items):
        start_time = time.time()
        try:
            result = perform_and_store(repo, it.op, it.numbers)
            duration_s = (time.time() - start_time) #! en segundos

            items_out.append({"index": idx, "status": "ok", "data": result})

            operations_counter.labels(operation=it.op, status='success').inc()
            operation_duration.labels(operation=it.op).observe(duration_s)
            logger.info(f"Batch [{idx}]: Operación '{it.op}' completada exitosamente - Números: {it.numbers}, Resultado: {result['result']}")
        except HTTPException as e:
            any_error = True
            duration_s = (time.time() - start_time) #! en segundos
            items_out.append({
                "index": idx,
                "status": "error",
                "error": e.detail,
                "status_code": e.status_code
            })
            operations_counter.labels(operation=it.op, status='error').inc()
            operation_duration.labels(operation=it.op).observe(duration_s)
            error_type = e.detail.get('code', 'UNKNOWN') if isinstance(e.detail, dict) else 'HTTP_ERROR'
            errors_counter.labels(error_type=error_type, operation=it.op).inc()
            logger.error(f"Batch [{idx}]: Error en operación '{it.op}' - Números: {it.numbers}, Error: {e.detail}")
        except Exception as e:
            any_error = True
            duration_s = (time.time() - start_time) #! en segundos
            error_detail = {"code":"UNEXPECTED","message":str(e)}
            items_out.append({
                "index": idx,
                "status": "error",
                "error": {"code":"UNEXPECTED","message":str(e)},
                "status_code": 500
            })
            operations_counter.labels(operation=it.op, status='error').inc()
            operation_duration.labels(operation=it.op).observe(duration_s)
            errors_counter.labels(error_type='UNEXPECTED', operation=it.op).inc()
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
        errors_counter.labels(error_type='INVALID_OPERATION', operation=op).inc()
        raise HTTPException(status_code=404, detail="operación inválida")
    start_time = time.time()
    try:
        result = perform_and_store(repo, op, body.numbers)
        duration_s = (time.time() - start_time) #! en segundos
        operations_counter.labels(operation=op, status='success').inc()
        operation_duration.labels(operation=op).observe(duration_s)
        logger.info(f"Operación '{op}' completada exitosamente - Números: {body.numbers}, Resultado: {result['result']}")
        return result
    except HTTPException as e:
        duration_s = (time.time() - start_time) #! en segundos
        operations_counter.labels(operation=op, status='error').inc()
        operation_duration.labels(operation=op).observe(duration_s)
        error_type = e.detail.get('code', 'UNKNOWN') if isinstance(e.detail, dict) else 'HTTP_ERROR'
        errors_counter.labels(error_type=error_type, operation=op).inc()
        logger.error(f"Error en operación '{op}' - Números: {body.numbers}, Error: {e.detail}")
        raise
    except Exception as e:
        duration_s = (time.time() - start_time) #! en segundos
        operations_counter.labels(operation=op, status='error').inc()
        operation_duration.labels(operation=op).observe(duration_s)
        errors_counter.labels(error_type='UNEXPECTED', operation=op).inc()
        logger.error(f"Error inesperado en operación '{op}' - Números: {body.numbers}, Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="error interno del servidor: " + str(e))

@app.get("/api/history", tags=["history"])
def history(filters: HistoryFilters = Depends(), repo: HistoryRepository = Depends(repo_dep)):
    try:
        logger.info(f"Obteniendo historial con filtros: op={filters.op}, date_from={filters.date_from}, date_to={filters.date_to}, sort_by={filters.sort_by}, order={filters.order}")
        items = repo.find(op=filters.op, date_from=filters.date_from, date_to=filters.date_to,
                    sort_by=filters.sort_by, order=filters.order)
        history_queries.labels(status='success').inc()
        logger.info(f"Historial obtenido: {len(items)} registros encontrados")
        return {"items": items}
    except Exception as e:
        history_queries.labels(status='error').inc()
        errors_counter.labels(error_type='DATABASE_ERROR', operation='history_query').inc()
        logger.error(f"Error inesperado al obtener historial - Filtros: op={filters.op}, date_from={filters.date_from}, date_to={filters.date_to}, sort_by={filters.sort_by}, order={filters.order}, Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="error interno del servidor: " + str(e))

@app.get("/health", tags=["health"])
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"msg": "API Calculadora funcionando!"}

# * Eventos de arranque y apagado
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando la aplicación Calc API")
    logger.info("Backend de Calculadora iniciada correctamente")
    get_process()  #* Inicializar proceso para métricas

@app.on_event("startup")
async def start_system_metrics_collector():
    # Lanzamos el loop de métricas de sistema como tarea de fondo
    asyncio.create_task(system_metrics_loop(interval_seconds=5))

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Apagando la aplicación Calc API")
    logger.info("Backend de Calculadora apagada correctamente")

