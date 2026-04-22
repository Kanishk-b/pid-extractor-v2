from pid_extraction.storage.artifact_store import ArtifactStore
from config.settings import Settings
from pid_extraction.logging_config import get_logger
from pid_extraction.components.c1_preprocessing.family_template import DrawingFamily
from pid_extraction.models.extraction import ExtractionResult
from pid_extraction.models.validation import ValidatedExtraction

from .rules.schema import SchemaRule
from .rules.dedupe import DedupeRule
from .rules.loops import LoopsRule
from .rules.statistics import StatisticsRule
from .rules.topology import TopologyRule
from .report import generate_report

logger = get_logger("c3_validator")

class Validator:
    def __init__(self, artifact_store: ArtifactStore, settings: Settings, family_template: DrawingFamily):
        self.store = artifact_store
        self.settings = settings
        self.family = family_template
        # The Complete Pipeline of Rules
        self.rules = [
            SchemaRule(), 
            DedupeRule(), 
            LoopsRule(), 
            StatisticsRule(), 
            TopologyRule()
        ]

    def run(self, drawing_id: str):
        logger.info("Starting C3 Validation", drawing_id=drawing_id)
        
        # Load C2 raw extractions
        raw_data = self.store.get_json(drawing_id, "03_extraction_raw.json")
        
        # Convert to ValidatedExtraction wrappers
        records = []
        for region_data in raw_data.get("regions", []):
            result = ExtractionResult(**region_data)
            for ext in result.extractions:
                records.append(ValidatedExtraction(extraction=ext, flags=[], dedupe_status="unique"))
                
        # Apply all Rules sequentially
        for rule in self.rules:
            records = rule.apply(records, self.family)
            
        # Save Validated JSON
        output_data = {"validated_extractions": [r.model_dump() for r in records]}
        self.store.put_json(drawing_id, "04_extraction_validated.json", output_data)
        
        # Generate and Save Report
        report_text = generate_report(drawing_id, records)
        self.store.put_bytes(drawing_id, "04_validation_report.txt", report_text.encode("utf-8"))
        
        logger.info("C3 Validation Complete", total_validated=len(records))
        return records