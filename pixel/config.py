import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}

class Settings:
    version = "3.5.0"
    model_provider = os.getenv("PIXEL_MODEL_PROVIDER", "local").strip().lower()
    model_name = os.getenv("PIXEL_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    api_base_url = os.getenv("PIXEL_API_BASE_URL", "http://127.0.0.1:11434/v1").strip().rstrip("/")
    api_key = os.getenv("PIXEL_API_KEY", "").strip()
    request_timeout = max(5, min(300, int(os.getenv("PIXEL_REQUEST_TIMEOUT", "90"))))
    db_path = str((ROOT / os.getenv("PIXEL_DB", "data/pixel.db")).resolve()) if not Path(os.getenv("PIXEL_DB", "data/pixel.db")).is_absolute() else os.getenv("PIXEL_DB")
    max_new_tokens = max(16, min(4096, int(os.getenv("PIXEL_MAX_NEW_TOKENS", "256"))))
    max_history_messages = max(2, min(100, int(os.getenv("PIXEL_MAX_HISTORY_MESSAGES", "16"))))
    chunk_size = max(100, min(10000, int(os.getenv("PIXEL_CHUNK_SIZE", "1800"))))
    chunk_overlap = max(0, min(2000, int(os.getenv("PIXEL_CHUNK_OVERLAP", "200"))))
    web_search_enabled = env_bool("PIXEL_WEB_SEARCH_ENABLED", True)
    vision_api_url = os.getenv("PIXEL_VISION_API_URL", "").strip()
    vision_api_key = os.getenv("PIXEL_VISION_API_KEY", "").strip()
    vision_model = os.getenv("PIXEL_VISION_MODEL", "").strip()
    host = os.getenv("PIXEL_HOST", "127.0.0.1")
    port = max(1, min(65535, int(os.getenv("PIXEL_PORT", "8000"))))

settings = Settings()
