from pathlib import Path
import json
INPUT = Path("data/training_examples.jsonl")
OUTPUT = Path("data/pixel_train.jsonl")

def main():
    if not INPUT.exists():
        print(f"Create {INPUT} first."); return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with INPUT.open(encoding="utf-8") as src, OUTPUT.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip(): continue
            item = json.loads(line)
            if "instruction" not in item or "output" not in item: continue
            dst.write(json.dumps({"messages":[{"role":"user","content":item["instruction"]},{"role":"assistant","content":item["output"]}]}, ensure_ascii=False) + "\n")
    print(f"Prepared dataset: {OUTPUT}")

if __name__ == "__main__": main()
