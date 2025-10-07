def test_sum_ok(client):
    r = client.post("/api/sum", json={"numbers":[1,2,3]})
    assert r.status_code == 200
    data = r.json()
    assert data["result"] == 6

def test_negatives_400(client):
    r = client.post("/api/mul", json={"numbers":[2,-1,3]})
    assert r.status_code == 400
    d = r.json()["detail"]
    assert d["code"] == "NEGATIVOS_NO_PERMITIDOS"
    assert d["op"] == "mul"
    assert d["numbers"] == [2,-1,3]

def test_division_by_zero_403(client):
    r = client.post("/api/div", json={"numbers":[10,0]})
    assert r.status_code == 403
    d = r.json()["detail"]
    assert d["code"] == "DIVISION_CERO"
