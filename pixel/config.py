import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("PIXEL_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    embedding_model: str = os.getenv("PIXEL_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    db_path: str = os.getenv("PIXEL_DB", "data/pixel.db")
    max_memory_results: int = int(os.getenv("PIXEL_MAX_MEMORY_RESULTS", "5"))
    max_new_tokens: int = int(os.getenv("PIXEL_MAX_NEW_TOKENS", "256"))

settings = Settings()
