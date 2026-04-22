class PidExtractionError(Exception):
    """Base exception for all PID Extraction errors."""
    pass

class PreprocessingError(PidExtractionError):
    pass

class PdfRasterizationError(PreprocessingError):
    pass

class RegionSegmentationError(PreprocessingError):
    pass

class ExtractionError(PidExtractionError):
    pass

class VlmApiError(ExtractionError):
    def __init__(self, provider: str, status: int, message: str):
        super().__init__(f"VLM API Error ({provider} - {status}): {message}")
        self.provider = provider
        self.status = status

class SchemaValidationError(ExtractionError):
    pass

class ValidationError(PidExtractionError):
    """Errors occurring during deterministic validation (C3)."""
    pass

class RoutingError(PidExtractionError):
    """Errors occurring during confidence routing (C4)."""
    pass