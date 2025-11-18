from fastapi import FastAPI, Depends, status, HTTPException, Request
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

app = FastAPI(title="Calc API")

_process = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# * Metricas pra prometheus

operations_counter = Counter(
    'calculator_operations_total',
    'Total de operaciones realizadas',
    ['operation', 'status']  #! labels: sum/sub/mul/div y success/error
)

# Histograma de duración de operaciones #! en segundos
operation_duration = Histogram(
    'calculator_operation_duration_seconds',
    'Duración de las operaciones en segundos',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
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
    """Actualiza métricas de CPU y memoria"""
    try:
        process = get_process()

        cpu = process.cpu_percent()
        if cpu == 0.0:
            #! Primera llamada retorna 0.0, hacer una segunda llamada rápida
            time.sleep(0.1)
            cpu = process.cpu_percent()
        cpu_usage.set(cpu)

        mem_info = process.memory_info()
        memory_usage.set(mem_info.rss)
        memory_percent.set(process.memory_percent())
        logger.info(f"Métricas de sistema actualizadas: CPU {cpu}%, Memoria {mem_info.rss} bytes ({process.memory_percent()}%)")
    except Exception as e:
        logger.error(f"Error actualizando métricas de sistema: {str(e)}")

def repo_dep(db=Depends(get_db)):
    return HistoryRepository(db["history"])

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

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando la aplicación Calc API")
    logger.info("Backend de Calculadora iniciada correctamente")
    get_process()  #* Inicializar proceso para métricas

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Apagando la aplicación Calc API")
    logger.info("Backend de Calculadora apagada correctamente")