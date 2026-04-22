from pydantic import BaseModel
from typing import Literal

class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int

class Region(BaseModel):
    region_id: str
    label: str
    global_bbox: BoundingBox
    file_path: str
    estimated_tag_density: Literal["low", "medium", "high"]
    secondary_tiling_applied: bool = False

class RegionManifest(BaseModel):
    drawing_id: str
    source_pdf: str
    rendered_at_dpi: int
    sheet_dimensions_px: dict[str, int]
    titleblock_crop: BoundingBox | None
    regions: list[Region]