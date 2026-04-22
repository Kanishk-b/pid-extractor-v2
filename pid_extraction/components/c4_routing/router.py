from pid_extraction.models.validation import ValidatedExtraction
from pid_extraction.models.review import Disposition
from .priority import calculate_priority

def route_record(record: ValidatedExtraction, drawing_under_extracted: bool) -> tuple[Disposition, float]:
    """Determines the disposition and priority of a record."""
    if drawing_under_extracted:
        return "review_queue", calculate_priority(record)

    conf = record.extraction.confidence
    hard_flags = [f for f in record.flags if f.severity == "hard"]
    soft_flags = [f for f in record.flags if f.severity == "soft"]

    # (confidence='low', 2+ hard flags) -> auto_reject
    if conf == "low" and len(hard_flags) >= 2:
        return "auto_reject", 0.0
        
    # (confidence=*, 1 hard flag) -> review_queue (priority=high)
    if hard_flags:
        return "review_queue", calculate_priority(record)

    # (confidence='high', no hard flags, 0 or 1 soft flag) -> auto_accept
    if conf == "high" and not hard_flags and len(soft_flags) <= 1:
        return "auto_accept", 0.0

    # (confidence='high', no hard flags, 2+ soft flags) -> review_queue
    if conf == "high" and not hard_flags and len(soft_flags) >= 2:
        return "review_queue", calculate_priority(record)

    # (confidence='medium' or 'low', no hard flags) -> review_queue
    if conf in ["medium", "low"] and not hard_flags:
        return "review_queue", calculate_priority(record)

    # Default fallback
    return "review_queue", calculate_priority(record)