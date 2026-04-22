import re
from .base import ValidationRule
from pid_extraction.models.validation import ValidatedExtraction, ValidationFlag
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily
from ..ocr_corrections import get_correction_candidates

class SchemaRule(ValidationRule):
    def apply(self, records: list[ValidatedExtraction], family: DrawingFamily) -> list[ValidatedExtraction]:
        compiled_patterns = {k: re.compile(v) for k, v in family.tag_schemas.items()}
        fallback_pattern = re.compile(r"^[A-Z0-9]+-[A-Z0-9]+$|^[A-Z]+[0-9]+$")

        for record in records:
            ext = record.extraction
            # Map the type to the regex schema name
            schema_key = f"{ext.type.upper()}_TAG" if ext.type in ["instrument", "equipment"] else None
            if ext.type == "note": schema_key = "NOTE_REF"
            
            pattern = compiled_patterns.get(schema_key, fallback_pattern)
            
            if pattern.match(ext.tag):
                record.flags.append(ValidationFlag(name="schema_valid", severity="soft", message="Tag format is valid."))
            else:
                record.flags.append(ValidationFlag(name="schema_failure", severity="hard", message=f"Does not match {schema_key} pattern."))
                # Try OCR correction
                correction = get_correction_candidates(ext.tag, pattern)
                if correction:
                    record.flags.append(ValidationFlag(name="ocr_correction_candidate", severity="soft", message=f"Proposed correction: {correction}"))
                    
        return records