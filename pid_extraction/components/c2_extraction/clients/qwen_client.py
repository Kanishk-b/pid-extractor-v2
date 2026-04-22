from openai import OpenAI
import base64
from config.settings import settings
from pid_extraction.exceptions import VlmApiError
from ..parsing import clean_and_parse_json

class QwenClient:
    def __init__(self):
        if not settings.QWEN_API_KEY and not settings.OPENAI_API_KEY:
            raise ValueError("API Key not set in environment variables.")
            
        api_key = settings.QWEN_API_KEY or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=api_key, base_url=settings.QWEN_API_BASE, timeout=120.0)
        self.model = settings.PRIMARY_MODEL

    # Changed return type to tuple: (parsed_dict, total_tokens_used)
    def extract(self, image: bytes, system_prompt: str, user_prompt: str, image_media_type: str = "image/jpeg") -> tuple[dict, int]:
        base64_image = base64.b64encode(image).decode('utf-8')
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:{image_media_type};base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.01
            )
            raw = response.choices[0].message.content
            
            # --- Capture the exact token count from the API response ---
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return clean_and_parse_json(raw), tokens_used
            
        except Exception as e:
            raise VlmApiError("Novita/Qwen", 500, str(e))