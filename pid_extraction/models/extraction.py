from pydantic import BaseModel
from typing import Literal, Any

class Extraction(BaseModel):
    id: str
    type: Literal["instrument", "equipment", "valve", "note"]
    tag: str
    isa_function: str | None = None
    approx_location: str
    associated_with: str | None = None
    confidence: Literal["high", "medium", "low"]
    reasoning: str
    region_id: str
    raw_model_output: dict[str, Any] | None = None

class ExtractionResult(BaseModel):
    region_id: str
    extractions: list[Extraction]
    uncertain_regions: list[str]
    model_used: str
    prompt_version: str
    review_notes: str | None = None