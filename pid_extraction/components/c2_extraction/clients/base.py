from typing import Protocol, Any

class VlmClient(Protocol):
    def extract(self, image: bytes, system_prompt: str, user_prompt: str, image_media_type: str = "image/png") -> dict[str, Any]:
        """Returns parsed JSON from the model response."""
        ...