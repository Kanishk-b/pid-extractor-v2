import json
from datetime import datetime
from pathlib import Path
from pid_extraction.models.extraction import Extraction

FEEDBACK_FILE = Path("feedback/corrections.jsonl")

def log_correction(drawing_id: str, extraction: Extraction, corrected_tag: str, notes: str, model: str, prompt_ver: str):
    FEEDBACK_FILE.parent.mkdir(exist_ok=True)
    
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "drawing_id": drawing_id,
        "region_id": extraction.region_id,
        "original_extraction": extraction.model_dump(),
        "corrected_tag": corrected_tag,
        "reviewer_notes": notes,
        "prompt_version": prompt_ver,
        "model_used": model
    }
    
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")