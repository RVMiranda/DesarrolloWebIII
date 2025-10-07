from pydantic import BaseModel, conlist
from typing import List, Literal, Optional
from datetime import datetime

Operation = Literal["sum", "sub", "mul", "div"]

class NumbersBody(BaseModel):
    numbers: conlist(float, min_length=1) 

class HistoryItem(BaseModel):
    id: str
    op: Operation
    numbers: List[float]
    result: float
    created_at: datetime

class BatchItem(BaseModel):
    op: Operation
    numbers: conlist(float, min_length=1)  

class BatchBody(BaseModel):
    items: conlist(BatchItem, min_length=1)

class HistoryFilters(BaseModel):
    op: Optional[Operation] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: Optional[Literal["date", "result"]] = "date"
    order: Optional[Literal["asc", "desc"]] = "desc"
