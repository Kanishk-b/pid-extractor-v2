from .base import ValidationRule
from pid_extraction.models.validation import ValidatedExtraction, ValidationFlag
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily

class TopologyRule(ValidationRule):
    def apply(self, records: list[ValidatedExtraction], family: DrawingFamily) -> list[ValidatedExtraction]:
        # Gather all explicit equipment tags extracted
        equipment_tags = [r.extraction.tag for r in records if r.extraction.type == "equipment"]
        vague_terms = ["line", "vessel", "pipe", "pump", "tank"]
        
        for record in records:
            ext = record.extraction
            
            if ext.type in ["instrument", "valve", "note"]:
                assoc = str(ext.associated_with).lower() if ext.associated_with else ""
                if not assoc or assoc in vague_terms:
                    record.flags.append(ValidationFlag(
                        name="topology_orphan", severity="soft", 
                        message=f"Lacks specific equipment/line association (currently: '{ext.associated_with}')."
                    ))
                    
            if ext.type == "equipment":
                # Check if ANY other record mentions this equipment
                has_assoc = any(ext.tag in str(r.extraction.associated_with) for r in records if r.extraction.id != ext.id)
                if not has_assoc:
                    record.flags.append(ValidationFlag(
                        name="equipment_without_instruments", severity="soft", 
                        message=f"No extracted instruments are associated with {ext.tag}."
                    ))
                    
        return records