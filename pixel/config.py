import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int, minimum: int = 1) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(value, minimum)


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("PIXEL_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    embedding_model: str = os.getenv(
        "PIXEL_EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    db_path: str = os.getenv("PIXEL_DB", "data/pixel.db")
    max_memory_results: int = _int_env("PIXEL_MAX_MEMORY_RESULTS", 5)
    max_history_messages: int = _int_env("PIXEL_MAX_HISTORY_MESSAGES", 12)
    max_new_tokens: int = _int_env("PIXEL_MAX_NEW_TOKENS", 256)
    memory_threshold: float = float(os.getenv("PIXEL_MEMORY_THRESHOLD", "0.25"))
    memory_duplicate_threshold: float = float(os.getenv("PIXEL_MEMORY_DUPLICATE_THRESHOLD", "0.94"))
    chunk_size: int = _int_env("PIXEL_CHUNK_SIZE", 1800)
    chunk_overlap: int = _int_env("PIXEL_CHUNK_OVERLAP", 200, 0)


settings = Settings()
