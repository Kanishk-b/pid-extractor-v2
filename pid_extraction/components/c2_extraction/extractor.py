from jinja2 import Template
from pathlib import Path
from pid_extraction.storage.artifact_store import ArtifactStore
from config.settings import Settings
from pid_extraction.logging_config import get_logger
from pid_extraction.models.region import RegionManifest
from pid_extraction.models.extraction import ExtractionResult, Extraction
from pid_extraction.components.c1_preprocessing.family_template import load_family

from .clients.qwen_client import QwenClient

logger = get_logger("c2_extractor")

class Extractor:
    def __init__(self, artifact_store: ArtifactStore, settings: Settings):
        self.store = artifact_store
        self.settings = settings
        self.client = QwenClient()
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.cost_per_million = 0.80 # $0.80 per 1M tokens

    def _load_template(self, filename: str) -> Template:
        return Template((self.prompts_dir / filename).read_text(encoding="utf-8"))

    def run(self, drawing_id: str, family_id: str, enable_self_review: bool = True) -> list[ExtractionResult]:
        logger.info("Starting C2 VLM Extraction", drawing_id=drawing_id)
        
        manifest_data = self.store.get_json(drawing_id, "02_regions/manifest.json", RegionManifest)
        family = load_family(family_id)
        
        system_prompt = (self.prompts_dir / "system_extractor.txt").read_text(encoding="utf-8")
        ctx_template = self._load_template("context_header.txt")
        task_template = self._load_template("task_extraction.txt")
        review_template = self._load_template("task_self_review.txt")
        
        results = []
        total_pipeline_tokens = 0 # Running counter for the entire drawing
        
        for region in manifest_data.regions:
            logger.info("Extracting region", region_id=region.region_id)
            img_bytes = self.store.get_bytes(drawing_id, region.file_path)
            
            context_header = ctx_template.render(
                project_name="NexTurn Default",
                drawing_id=drawing_id,
                convention=family.convention,
                equipment_family=family.equipment_family,
                region_label=region.label,
                tag_schemas=family.tag_schemas,
                example_tags=family.example_tags,
                symbol_vocabulary=family.symbol_vocabulary
            )
            
            user_prompt = context_header + "\n\n" + task_template.render(region_id=region.region_id)
            
            # 1. First Pass
            try:
                # Unpack the tuple to grab the token count
                first_pass_json, pass_1_tokens = self.client.extract(img_bytes, system_prompt, user_prompt)
                total_pipeline_tokens += pass_1_tokens
            except Exception as e:
                logger.error("VLM Extraction Failed", region_id=region.region_id, error=str(e))
                continue
                
            # 2. Self-Review Pass
            final_json = first_pass_json
            if enable_self_review:
                logger.info("Running self-review", region_id=region.region_id)
                import json
                review_prompt = context_header + "\n\n" + review_template.render(first_pass_json=json.dumps(first_pass_json, indent=2))
                try:
                    final_json, pass_2_tokens = self.client.extract(img_bytes, system_prompt, review_prompt)
                    total_pipeline_tokens += pass_2_tokens
                except Exception as e:
                    logger.warning("Self-review failed, falling back to first pass", region_id=region.region_id)
            
            # 3. Map to Pydantic
            try:
                raw_extractions = final_json.get("extractions", [])
                for idx, ext in enumerate(raw_extractions):
                    ext["region_id"] = region.region_id 
                    ext["id"] = f"{region.region_id}_{idx + 1}"

                result = ExtractionResult(
                    region_id=region.region_id,
                    extractions=[Extraction(**ext) for ext in raw_extractions],
                    uncertain_regions=final_json.get("uncertain_regions", []),
                    model_used=self.settings.PRIMARY_MODEL,
                    prompt_version="c2-extraction-v1.1.0",
                    review_notes=final_json.get("review_notes")
                )
                results.append(result)
            except Exception as e:
                logger.error("Failed to map JSON to Pydantic Model", error=str(e))
                
        # --- The Cost Calculation ---
        total_cost_usd = (total_pipeline_tokens / 1_000_000) * self.cost_per_million
        
        # Save results, including the metadata!
        self.store.put_json(drawing_id, "03_extraction_raw.json", {
            "metadata": {
                "total_tokens_consumed": total_pipeline_tokens,
                "estimated_cost_usd": round(total_cost_usd, 4)
            },
            "regions": [r.model_dump() for r in results]
        })
        
        # Log it so you can see it live!
        logger.info("C2 Extraction Complete", 
                    total_regions=len(results), 
                    total_tokens=total_pipeline_tokens, 
                    cost_usd=f"${total_cost_usd:.4f}")
        
        return results