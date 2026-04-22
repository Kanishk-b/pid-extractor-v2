from datetime import datetime
from pid_extraction.storage.artifact_store import ArtifactStore
from pid_extraction.models.validation import ValidatedExtraction
from .router import route_record
from .feedback import log_correction

class QueueManager:
    def __init__(self, artifact_store: ArtifactStore):
        self.store = artifact_store

    def route_drawing(self, drawing_id: str):
        """Processes C3 validation output and creates the initial review state."""
        val_data = self.store.get_json(drawing_id, "04_extraction_validated.json")
        records = [ValidatedExtraction(**r) for r in val_data.get("validated_extractions", [])]
        
        # Check for drawing-level flags
        drawing_under_extracted = any(
            f.name == "statistical_under_extraction" for r in records for f in r.flags
        )

        state_items = []
        summary = {"auto_accepted": 0, "pending_review": 0, "auto_rejected": 0}

        for record in records:
            disposition, priority = route_record(record, drawing_under_extracted)
            
            # Update summary counts
            if disposition == "auto_accept": summary["auto_accepted"] += 1
            elif disposition == "auto_reject": summary["auto_rejected"] += 1
            else: summary["pending_review"] += 1

            status = "decided" if disposition in ["auto_accept", "auto_reject"] else "pending"
            
            state_items.append({
                "extraction_id": record.extraction.id,
                "disposition": disposition,
                "priority": priority,
                "status": status,
                "assigned_to": None,
                "created_at": datetime.utcnow().isoformat(),
                "decided_at": datetime.utcnow().isoformat() if status == "decided" else None,
                "reviewer_decision": disposition if status == "decided" else None,
                "corrected_tag": None,
                "notes": None
            })

        state = {
            "drawing_id": drawing_id,
            "items": state_items,
            "summary": summary
        }
        self.store.put_json(drawing_id, "05_review_state.json", state)
        return state