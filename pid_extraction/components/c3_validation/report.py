from pid_extraction.models.validation import ValidatedExtraction

def generate_report(drawing_id: str, records: list[ValidatedExtraction]) -> str:
    total = len(records)
    hard_flags = sum(1 for r in records if any(f.severity == "hard" for f in r.flags))
    schema_valid = total - hard_flags
    
    return f"""Drawing {drawing_id}
Extracted     : {total} tags
Schema valid  : {schema_valid} / {total} ({hard_flags} flagged for review)
"""