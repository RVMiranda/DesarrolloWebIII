def test_history_filters_and_sort(client):
    #conteo inicial de operaciones mul
    r_initial = client.get("/api/history", params={"op":"mul"})
    initial_mul_count = len(r_initial.json()["items"])
    
    client.post("/api/sum", json={"numbers":[1,2]})
    r_mul = client.post("/api/mul", json={"numbers":[2,3]})
    
    #se checa si la nueva operación mul se agregó
    r = client.get("/api/history", params={"op":"mul","sort_by":"result","order":"desc"})
    assert r.status_code == 200
    items = r.json()["items"]
    
    #al menos una operación mul más que al inicio
    assert len(items) >= initial_mul_count + 1
    
    #las operaciones devueltas son de tipo "mul"
    for item in items:
        assert item["op"] == "mul"
    
    #se checa si el resultado específico está en la lista
    mul_result = r_mul.json()["result"]
    results = [item["result"] for item in items]
    assert mul_result in results
    
    #resultado descendente
    for i in range(len(results) - 1):
        assert results[i] >= results[i + 1]
