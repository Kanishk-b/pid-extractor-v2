from .base import ValidationRule
from pid_extraction.models.validation import ValidatedExtraction, ValidationFlag
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily

class StatisticsRule(ValidationRule):
    def apply(self, records: list[ValidatedExtraction], family: DrawingFamily) -> list[ValidatedExtraction]:
        actual_count = len(records)
        expected_mean = family.expected_tag_count.get("mean", 0)
        expected_stddev = family.expected_tag_count.get("stddev", 0)
        
        if expected_mean == 0:
            return records
            
        lower_bound = expected_mean - (2 * expected_stddev)
        upper_bound = expected_mean + (2 * expected_stddev)
        
        drawing_flag = None
        if actual_count < lower_bound:
            drawing_flag = ValidationFlag(
                name="statistical_under_extraction", severity="hard", 
                message=f"Found {actual_count} tags, expected at least {lower_bound}. The AI may have missed dense regions."
            )
        elif actual_count > upper_bound:
            drawing_flag = ValidationFlag(
                name="statistical_over_extraction", severity="soft", 
                message=f"Found {actual_count} tags, expected at most {upper_bound}. Potential hallucination cluster."
            )
            
        # If the drawing is flagged statistically, apply it to all records to trigger drawing-level escalation
        if drawing_flag:
            for record in records:
                record.flags.append(drawing_flag)
                
        return records