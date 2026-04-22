from pid_extraction.storage.artifact_store import ArtifactStore

def emit_final(drawing_id: str, artifact_store: ArtifactStore):
    state = artifact_store.get_json(drawing_id, "05_review_state.json")
    val_data = artifact_store.get_json(drawing_id, "04_extraction_validated.json")
    
    # Map extractions by ID
    extracted_map = {r["extraction"]["id"]: r["extraction"] for r in val_data.get("validated_extractions", [])}
    
    final_records = []
    
    for item in state.get("items", []):
        # We only keep auto_accept and reviewer accept/correct
        if item["disposition"] == "auto_accept" or item["reviewer_decision"] in ["accept", "correct"]:
            base_extraction = extracted_map[item["extraction_id"]]
            
            # Apply corrections if present
            if item["reviewer_decision"] == "correct" and item["corrected_tag"]:
                base_extraction["tag"] = item["corrected_tag"]
                
            final_records.append(base_extraction)
            
    artifact_store.put_json(drawing_id, "06_final.json", {"final_extractions": final_records})
    return final_records