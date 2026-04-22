from pid_extraction.models.validation import ValidatedExtraction

def calculate_priority(record: ValidatedExtraction, age_in_queue_hours: float = 0.0) -> float:
    """Calculates the review priority score."""
    is_low_confidence = 1 if record.extraction.confidence == "low" else 0
    has_schema_failure = 1 if any(f.name == "schema_failure" for f in record.flags) else 0
    has_topology_anomaly = 1 if any("topology" in f.name for f in record.flags) else 0
    has_loop_inconsistency = 1 if any("loop" in f.name for f in record.flags) else 0
    is_equipment = 1 if record.extraction.type == "equipment" else 0
    
    priority = (
        (3 * is_low_confidence) +
        (2 * has_schema_failure) +
        (1 * has_topology_anomaly) +
        (1 * has_loop_inconsistency) +
        (2 * is_equipment) -
        (0.05 * age_in_queue_hours)
    )
    return round(priority, 2)