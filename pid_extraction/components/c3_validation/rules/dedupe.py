from .base import ValidationRule
from pid_extraction.models.validation import ValidatedExtraction, ValidationFlag
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily
from collections import defaultdict

class DedupeRule(ValidationRule):
    def apply(self, records: list[ValidatedExtraction], family: DrawingFamily) -> list[ValidatedExtraction]:
        grouped = defaultdict(list)
        for record in records:
            grouped[record.extraction.tag].append(record)
            
        final_records = []
        for tag, group in grouped.items():
            if len(group) == 1:
                group[0].dedupe_status = "unique"
                final_records.append(group[0])
            else:
                # Find the highest confidence extraction to act as the "base"
                high_conf = [r for r in group if r.extraction.confidence == "high"]
                canonical = high_conf[0] if high_conf else group[0]
                
                # Combine the region history so we don't lose where it was found
                all_regions = sorted(list(set(r.extraction.region_id for r in group)))
                canonical.extraction.region_id = ", ".join(all_regions)
                
                canonical.dedupe_status = "merged"
                canonical.flags.append(
                    ValidationFlag(
                        name="merged_duplicate", 
                        severity="soft", 
                        message=f"Merged {len(group)} occurrences across regions: {all_regions}"
                    )
                )
                final_records.append(canonical)
                
        return final_records