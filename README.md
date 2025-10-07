# Calculadora n números — FastAPI + MongoDB + React + Docker

## Levantar con Docker
```bash
docker-compose up --build
```
- API: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Endpoints
- `POST /api/sum|sub|mul|div` body: `{"numbers":[...]}`
- `GET /api/history?op=&date_from=&date_to=&sort_by=date|result&order=asc|desc`
- `POST /api/batch` body:
```json
{
  "items":[
    {"op":"sum","numbers":[1,2,3]},
    {"op":"div","numbers":[8,2]}
  ]
}
```
### Comportamiento de /batch
- **Procesa todo**: guarda en historial los que sean válidos.
- **Acumula errores por ítem**: responde con `status 207` (Multi-Status) si hubo al menos un error.
- Respuesta ejemplo:
```json
{
  "items":[
    {"index":0,"status":"ok","data":{"id":"...","op":"sum","numbers":[1,2,3],"result":6}},
    {"index":1,"status":"error","error":{"code":"DIVISION_BY_ZERO","message":"División entre cero no permitida","op":"div","numbers":[8,0]},"status_code":403}
  ]
}
```

## Pruebas
Dentro de `backend/`:
```bash
pytest -q
```

## Variables de entorno
- `MONGO_URI` (backend): por defecto `mongodb://admin_user:web3@mongo:27017/?authSource=admin`

## Notas
- Números negativos -> 400 con JSON `{code:"NEGATIVE_NOT_ALLOWED",...}`
- División entre cero -> 403 con JSON `{code:"DIVISION_BY_ZERO",...}`

## Cambios
- Cambio para verificar github actions