from PIL import Image, ImageEnhance

def enhance_contrast(img: Image.Image) -> Image.Image:
    """Applies Grayscale, Contrast, and Sharpness filters."""
    # Convert to greyscale
    img = img.convert('L')
    
    # Boost contrast
    img = ImageEnhance.Contrast(img).enhance(2.0)
    
    # Boost sharpness
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    
    # Convert back to RGB for downstream processing
    return img.convert('RGB')