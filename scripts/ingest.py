from pathlib import Path
import csv, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pixel.brain import PixelBrain
ROOT = Path("data/knowledge")

def read_file(path):
    if path.suffix.lower() in {".txt", ".md"}: return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json": return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as f: return "\n".join(",".join(row) for row in csv.reader(f))
    return ""

def main():
    ROOT.mkdir(parents=True, exist_ok=True); brain = PixelBrain(); count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file(): continue
        text = read_file(path).strip()
        for start in range(0, len(text), 2500):
            chunk = text[start:start+2500].strip()
            if chunk: brain.learn(chunk, str(path)); count += 1
    print(f"Imported {count} knowledge chunks.")

if __name__ == "__main__": main()
