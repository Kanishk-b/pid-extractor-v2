import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path
from pid_extraction.storage.artifact_store import ArtifactStore
from config.settings import Settings
from pid_extraction.logging_config import get_logger
# Now importing your advanced schemas perfectly:
from pid_extraction.models.region import RegionManifest, Region, BoundingBox

logger = get_logger("c1_preprocessor")

class Preprocessor:
    def __init__(self, artifact_store: ArtifactStore, settings: Settings):
        self.store = artifact_store
        self.settings = settings
        self.dpi = 300
        self.overlap_ratio = 0.15 # 15% overlap so edge tags aren't cut in half

    def run(self, drawing_id: str, family_id: str) -> RegionManifest:
        logger.info("Starting C1 Preprocessing", drawing_id=drawing_id, family_id=family_id)
        
        pdf_bytes = self.store.get_bytes(drawing_id, "01_source.pdf")
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)
        
        # Rasterize at high DPI
        zoom = self.dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        width, height = img.size
        logger.info("Rasterization complete", size=(width, height))
        
        # Calculate 3x3 grid dimensions with overlap
        step_x = int(width / 3)
        step_y = int(height / 3)
        overlap_x = int(step_x * self.overlap_ratio)
        overlap_y = int(step_y * self.overlap_ratio)
        
        regions = []
        labels = [
            "top_left", "top_center", "top_right",
            "middle_left", "center", "middle_right",
            "bottom_left", "bottom_center", "bottom_right"
        ]
        
        idx = 0
        for row in range(3):
            for col in range(3):
                # Calculate bounding box with overlap
                left = max(0, col * step_x - (overlap_x if col > 0 else 0))
                top = max(0, row * step_y - (overlap_y if row > 0 else 0))
                right = min(width, (col + 1) * step_x + (overlap_x if col < 2 else 0))
                bottom = min(height, (row + 1) * step_y + (overlap_y if row < 2 else 0))
                
                box = (left, top, right, bottom)
                region_img = img.crop(box)
                
                region_id = f"R{idx+1:02d}"
                label = labels[idx]
                file_path = f"02_regions/{region_id}.png"
                
                img_byte_arr = io.BytesIO()
                region_img.save(img_byte_arr, format='PNG')
                self.store.put_bytes(drawing_id, file_path, img_byte_arr.getvalue())
                
                # Mapping to your strict BoundingBox model
                bbox = BoundingBox(x=left, y=top, w=(right-left), h=(bottom-top))
                
                # Mapping to your strict Region model
                regions.append(Region(
                    region_id=region_id,
                    label=label,
                    global_bbox=bbox,
                    file_path=file_path,
                    estimated_tag_density="medium",
                    secondary_tiling_applied=False
                ))
                logger.info("Saved region", label=label, region_id=region_id)
                idx += 1
                
        # Mapping to your strict RegionManifest model
        manifest = RegionManifest(
            drawing_id=drawing_id,
            source_pdf="01_source.pdf",
            rendered_at_dpi=self.dpi,
            sheet_dimensions_px={"width": width, "height": height},
            titleblock_crop=None,
            regions=regions
        )
        
        self.store.put_json(drawing_id, "02_regions/manifest.json", manifest.model_dump())
        logger.info("C1 Preprocessing Complete", region_count=len(regions))
        
        return manifest