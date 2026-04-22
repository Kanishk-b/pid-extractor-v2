from pydantic import BaseModel
from typing import Literal
from .extraction import Extraction

class ValidationFlag(BaseModel):
    name: str
    severity: Literal["soft", "hard"]
    message: str

class ValidatedExtraction(BaseModel):
    extraction: Extraction
    flags: list[ValidationFlag]
    dedupe_status: Literal["unique", "merged", "flagged_distant"]