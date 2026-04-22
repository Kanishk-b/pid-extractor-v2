import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Any

class DrawingFamily(BaseModel):
    family_id: str
    family_name: str
    description: str
    convention: str
    equipment_family: str
    tag_schemas: dict[str, str]
    symbol_vocabulary: list[list[str]]
    region_template: list[list[Any]] # [label, [x1, y1, x2, y2]]
    expected_tag_count: dict[str, int]
    example_tags: list[str]

def load_family(family_id: str) -> DrawingFamily:
    """Loads the YAML configuration for a specific drawing family."""
    path = Path(f"config/drawing_families/{family_id}.yaml")
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return DrawingFamily(**data)