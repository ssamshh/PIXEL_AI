from pathlib import Path
import csv
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pixel.brain import PixelBrain
from pixel.config import settings

ROOT = Path("data/knowledge")


def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".json":
        return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)
    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return "\n".join(",".join(row) for row in csv.reader(handle))
    return ""


def chunks(text: str):
    size = settings.chunk_size
    overlap = min(settings.chunk_overlap, size - 1)
    step = size - overlap
    for start in range(0, len(text), step):
        chunk = text[start:start + size].strip()
        if chunk:
            yield chunk


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    brain = PixelBrain()
    count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        text = read_file(path).strip()
        for chunk in chunks(text):
            result = brain.learn(chunk, source=str(path), category="knowledge")
            if result["status"] == "stored":
                count += 1
    print(f"Imported {count} new knowledge chunks.")


if __name__ == "__main__":
    main()
