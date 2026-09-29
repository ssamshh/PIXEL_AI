# PIXEL AI

PIXEL is a modular Deep Learning AI assistant with local text generation, semantic memory, RAG, a REST API, and a CLI.

## What makes PIXEL useful

- Persian/English conversation
- Local Deep Learning language model
- Long-term semantic memory
- RAG: retrieves relevant stored knowledge before answering
- Import TXT/MD/JSON/CSV knowledge
- SQLite conversation history
- API for connecting a website, bot, or app
- Dataset preparation for later fine-tuning
- Optional PEFT/LoRA stack for future model adaptation

## Important design choice

PIXEL has two different kinds of learning:

1. **Memory learning**: new knowledge is embedded and stored immediately. This does not retrain the model.
2. **Weight learning**: approved examples can later be used for LoRA fine-tuning. This changes adapter weights and is slower.

Separating these makes PIXEL much easier to maintain and reduces the risk of blindly retraining the model on every message.

## Install

```bash
git clone https://github.com/YOUR_USERNAME/PIXEL-AI.git
cd PIXEL-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

CLI:

```bash
python -m pixel.cli
```

API:

```bash
uvicorn pixel.api:app --host 0.0.0.0 --port 8000
```

Docs: `http://127.0.0.1:8000/docs`

## Teach PIXEL

In CLI:

```text
/learn PIXEL is my AI project.
```

Or API:

```bash
curl -X POST http://127.0.0.1:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"text":"PIXEL is my AI project.","source":"manual"}'
```

To import files, place them in `data/knowledge/` and run:

```bash
python scripts/ingest.py
```

## GitHub

Do not upload `.env`, passwords, private datasets, or generated model weights unless you intentionally want them public.

```bash
git add .
git commit -m "Initial PIXEL AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/PIXEL-AI.git
git push -u origin main
```

## Roadmap

- Web UI
- Vision model
- Speech input/output
- Tool calling
- LoRA training pipeline
- Evaluation and safety tests
- Authentication and multi-user memory
- Plugin system

> No AI system can honestly guarantee zero bugs or perfect answers. PIXEL is designed to be modular, testable, and easier to debug.
