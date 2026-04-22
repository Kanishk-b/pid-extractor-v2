from PIL import Image
from pid_extraction.models.region import Region, BoundingBox

def segment_by_template(img: Image.Image, region_templates: list, region_id_prefix: str = "R") -> list[tuple[Region, Image.Image]]:
    """Slices the image into regions based on normalized bounding boxes in the template."""
    width, height = img.size
    regions_and_crops = []
    
    for idx, (label, bbox_fractions) in enumerate(region_templates):
        # Unpack the fractions [x1, y1, x2, y2]
        x1_frac, y1_frac, x2_frac, y2_frac = bbox_fractions
        
        # Convert fractions to actual pixels
        x1, y1 = int(x1_frac * width), int(y1_frac * height)
        x2, y2 = int(x2_frac * width), int(y2_frac * height)
        
        # Create BoundingBox model
        global_bbox = BoundingBox(x=x1, y=y1, w=x2-x1, h=y2-y1)
        
        # Crop the image
        crop = img.crop((x1, y1, x2, y2))
        
        # Create Region metadata
        region_id = f"{region_id_prefix}{idx+1:02d}"
        file_path = f"02_regions/{region_id}_{label}.png"
        
        region_model = Region(
            region_id=region_id,
            label=label,
            global_bbox=global_bbox,
            file_path=file_path,
            estimated_tag_density="medium" # Defaulting to medium for now
        )
        
        regions_and_crops.append((region_model, crop))
        
    return regions_and_crops