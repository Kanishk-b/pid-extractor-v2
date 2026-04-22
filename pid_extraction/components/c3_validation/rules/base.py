from typing import Protocol
from pid_extraction.models.validation import ValidatedExtraction
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily

class ValidationRule(Protocol):
    def apply(self, records: list[ValidatedExtraction], family: DrawingFamily) -> list[ValidatedExtraction]:
        ...