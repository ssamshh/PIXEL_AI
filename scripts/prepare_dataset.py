from pathlib import Path
import json

INPUT = Path("data/training_examples.jsonl")
OUTPUT = Path("data/pixel_train.jsonl")


def main():
    if not INPUT.exists():
        print(f"Create {INPUT} first.")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with INPUT.open(encoding="utf-8") as src, OUTPUT.open("w", encoding="utf-8") as dst:
        for line_number, line in enumerate(src, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Skipping line {line_number}: {exc}")
                continue
            instruction = item.get("instruction")
            output = item.get("output")
            if not instruction or not output:
                continue
            dst.write(json.dumps({"messages": [
                {"role": "user", "content": instruction},
                {"role": "assistant", "content": output},
            ]}, ensure_ascii=False) + "\n")
            written += 1
    print(f"Prepared dataset: {OUTPUT} ({written} examples)")


if __name__ == "__main__":
    main()
