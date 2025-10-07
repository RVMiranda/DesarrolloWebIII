from fastapi import FastAPI, Depends, status, HTTPException  # <-- unificamos import
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schemas import NumbersBody, HistoryFilters, BatchBody
from .deps import get_db
from .repository import HistoryRepository
from .services import perform_and_store

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
    items_out = []
    any_error = False
    for idx, it in enumerate(body.items):
        try:
            result = perform_and_store(repo, it.op, it.numbers)
            items_out.append({"index": idx, "status": "ok", "data": result})
        except HTTPException as e:
            any_error = True
            items_out.append({
                "index": idx,
                "status": "error",
                "error": e.detail,
                "status_code": e.status_code
            })
        except Exception as e:
            any_error = True
            items_out.append({
                "index": idx,
                "status": "error",
                "error": {"code":"UNEXPECTED","message":str(e)},
                "status_code": 500
            })
    http_code = getattr(status, "HTTP_207_MULTI_STATUS", 207)
    if not any_error:
        http_code = status.HTTP_200_OK
    return JSONResponse(status_code=http_code, content={"items": items_out})


@app.post("/api/{op}", tags=["operations"])
def operation(op: str, body: NumbersBody, repo: HistoryRepository = Depends(repo_dep)):
    if op not in {"sum","sub","mul","div"}:
        raise HTTPException(status_code=404, detail="operación inválida")
    return perform_and_store(repo, op, body.numbers)

@app.get("/api/history", tags=["history"])
def history(filters: HistoryFilters = Depends(), repo: HistoryRepository = Depends(repo_dep)):
    items = repo.find(op=filters.op, date_from=filters.date_from, date_to=filters.date_to,
                    sort_by=filters.sort_by, order=filters.order)
    return {"items": items}

@app.get("/health", tags=["health"])
def health():
    return {"ok": True}

