from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    QWEN_API_BASE: str = "https://api.novita.ai/v3/openai"
    QWEN_API_KEY: Optional[str] = None
    
    # Engine Settings
    PRIMARY_MODEL: str = "qwen/qwen2.5-vl-72b-instruct"
    ARTIFACT_STORE_ROOT: str = "./artifacts"
    LOG_LEVEL: str = "INFO"
    POPPLER_PATH: Optional[str] = None
    DEFAULT_RENDER_DPI: int = 400

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()