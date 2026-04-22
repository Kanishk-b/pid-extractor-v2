from pydantic import BaseModel
from typing import Literal
from datetime import datetime

Disposition = Literal["auto_accept", "review_queue", "auto_reject"]

class ReviewRecord(BaseModel):
    extraction_id: str
    disposition: Disposition
    priority_score: float
    assigned_to: str | None = None
    reviewer_decision: str | None = None
    corrected_tag: str | None = None
    decided_at: datetime | None = None