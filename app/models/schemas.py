from pydantic import BaseModel
from typing import List, Any


class Evidence(BaseModel):
    text: str


class IssueResult(BaseModel):
    category_id: str
    category_name: str
    severity: str
    confidence: float
    evidence: List[str]
    root_causes: List[str]
    next_steps: List[str]


class RunRecord(BaseModel):
    id: int
    timestamp: str
    input_summary: Any
    result: Any
