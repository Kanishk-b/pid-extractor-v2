import fitz  # PyMuPDF
from PIL import Image
import io
from pid_extraction.exceptions import PdfRasterizationError

def rasterize_pdf(pdf_bytes: bytes, dpi: int = 400) -> Image.Image:
    """Converts the first page of a PDF into a PIL Image."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if not doc:
            raise PdfRasterizationError("Could not open PDF bytes.")
        
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=dpi)
        img_data = pix.tobytes("png")
        
        img = Image.open(io.BytesIO(img_data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        return img
    except Exception as e:
        raise PdfRasterizationError(f"Failed to rasterize PDF: {e}")