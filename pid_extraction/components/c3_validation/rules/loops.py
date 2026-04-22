import re
from collections import defaultdict
from .base import ValidationRule
from pid_extraction.models.validation import ValidatedExtraction, ValidationFlag
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily

class LoopsRule(ValidationRule):
    def apply(self, records: list[ValidatedExtraction], family: DrawingFamily) -> list[ValidatedExtraction]:
        # Group instruments/valves by their loop number (e.g., "890" from "75LT-890")
        loop_groups = defaultdict(list)
        loop_regex = re.compile(r"-(\d{3,4})[A-Z]?$")
        
        for record in records:
            if record.extraction.type in ["instrument", "valve"]:
                match = loop_regex.search(record.extraction.tag)
                if match:
                    loop_groups[match.group(1)].append(record)
                    
        # Apply Loop Rules
        for loop_num, group in loop_groups.items():
            functions = [r.extraction.tag.split('-')[0] for r in group] # e.g., ["75LT", "75LIC"]
            functions_str = " ".join(functions)
            
            for record in group:
                tag = record.extraction.tag
                
                # Rule: CTRL_NEEDS_XMIT
                if any(c in tag for c in ["IC", "LIC", "PIC", "TIC", "FIC"]):
                    if not any(t in functions_str for t in ["IT", "LT", "PT", "TT", "FT"]):
                        record.flags.append(ValidationFlag(
                            name="loop_missing_transmitter", severity="soft", 
                            message=f"Controller {tag} is missing a corresponding Transmitter in loop {loop_num}."
                        ))
                
                # Rule: CV_NEEDS_CTRL
                if any(v in tag for v in ["LV", "PV", "TV", "FV"]):
                    if not any(c in functions_str for c in ["IC", "LIC", "PIC", "TIC", "FIC"]):
                        record.flags.append(ValidationFlag(
                            name="loop_missing_controller", severity="soft", 
                            message=f"Valve {tag} is missing a corresponding Controller in loop {loop_num}."
                        ))
                        
                # Rule: ORPHAN_TAG
                if len(group) == 1 and any(c in tag for c in ["IC", "ALARM"]):
                    record.flags.append(ValidationFlag(
                        name="loop_orphan", severity="soft", 
                        message=f"Tag {tag} is the only instrument in loop {loop_num} but typically belongs to a multi-tag loop."
                    ))
                    
        return records