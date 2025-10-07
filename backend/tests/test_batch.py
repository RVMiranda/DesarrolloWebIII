def test_batch_accumulates_errors_and_saves_successes(client):
    body = {"items":[
        {"op":"sum","numbers":[1,2,3]},        # deberia dar ok -> 6
        {"op":"div","numbers":[8,0]},          # debe dar error
        {"op":"mul","numbers":[2,3]},          # deberia dar ok -> 6
        {"op":"mul","numbers":[-1,5]}          # debe dar error
    ]}
    r = client.post("/api/batch", json=body)
    assert r.status_code == 207
    data = r.json()
    assert "items" in data
    # debemos tener 4 entradas
    assert len(data["items"]) == 4
    statuses = [it["status"] for it in data["items"]]
    assert statuses == ["ok","error","ok","error"]
    # valida que los ok traen result
    oks = [it for it in data["items"] if it["status"]=="ok"]
    assert oks[0]["data"]["result"] == 6
    assert oks[1]["data"]["result"] == 6
