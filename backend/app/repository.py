from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo.collection import Collection

class HistoryRepository:
    def __init__(self, col: Collection):
        self.col = col
        try:
            self.col.create_index("op")
            self.col.create_index("created_at")
        except:            
            pass

    def insert(self, op: str, numbers: List[float], result: float) -> str:
        doc = {"op": op, "numbers": numbers, "result": result, "created_at": datetime.utcnow()}
        ins = self.col.insert_one(doc)
        return str(ins.inserted_id)

    def find(self, *, op: Optional[str], date_from: Optional[datetime], date_to: Optional[datetime],
            sort_by: str, order: str) -> List[Dict[str, Any]]:
        q: Dict[str, Any] = {}
        if op: q["op"] = op
        if date_from or date_to:
            q["created_at"] = {}
            if date_from: q["created_at"]["$gte"] = date_from
            if date_to: q["created_at"]["$lte"] = date_to
        sort_field = "created_at" if sort_by == "date" else "result"
        direction = 1 if order == "asc" else -1
        cur = self.col.find(q).sort(sort_field, direction)
        return [
            {"id": str(d["_id"]), "op": d["op"], "numbers": d["numbers"],
                "result": d["result"], "created_at": d["created_at"]}
            for d in cur
        ]
