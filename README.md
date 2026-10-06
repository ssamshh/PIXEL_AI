# PIXEL AI 2.0

PIXEL is a modular local AI assistant built around a language model, semantic memory, retrieval-augmented generation (RAG), persistent conversation history, and a REST API.

## Highlights

- Local LLM inference with Hugging Face Transformers
- Persistent SQLite memory
- Semantic memory search with Sentence Transformers
- Duplicate-memory detection
- Memory categories and importance levels
- Conversation sessions with persistent history
- Memory CRUD: list, search, and forget
- Knowledge ingestion from TXT, Markdown, JSON, and CSV
- FastAPI REST API
- Interactive CLI
- CUDA acceleration when available
- Dataset preparation foundation for future fine-tuning
- Backward-compatible SQLite schema migration from PIXEL 1.x

## Architecture

```text
User
  |
  v
CLI / FastAPI
  |
  v
PIXEL Brain
  +--> Conversation History --> SQLite
  +--> Semantic Memory -------> SQLite + embeddings
  +--> RAG context ------------> LLM
  |
  v
Local Transformer Model
  |
  v
Response
```

## Install

```bash
git clone git@github.com:ssamshh/PIXEL_AI.git
cd PIXEL_AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The first run downloads the configured language and embedding models from Hugging Face.

## CLI

```bash
python -m pixel.cli
```

Commands:

```text
/learn TEXT       store a memory
/memory           list memories
/search TEXT      semantic memory search
/forget ID        delete a memory
/clear            clear the current conversation
/session NAME     switch session
/model            show model/device status
/help             show commands
/quit             exit
```

## API

Run:

```bash
uvicorn pixel.api:app --reload
```

Endpoints:

- `GET /`
- `GET /health`
- `POST /chat`
- `POST /learn`
- `GET /memory`
- `GET /memory/search?q=...`
- `DELETE /memory/{id}`
- `DELETE /chat/{session_id}`

Interactive API documentation is available at `/docs` while the server is running.

## Knowledge ingestion

Put `.txt`, `.md`, `.json`, or `.csv` files into `data/knowledge/`, then run:

```bash
python scripts/ingest.py
```

PIXEL splits large files into overlapping chunks and stores them as semantic memories.

## Dataset preparation

Create `data/training_examples.jsonl` using the example format, then run:

```bash
python scripts/prepare_dataset.py
```

This prepares conversational examples for a future PEFT/LoRA fine-tuning pipeline. Memory learning and model-weight training are intentionally separate systems.

## Configuration

All runtime settings are available through `.env`. The default model is `Qwen/Qwen2.5-0.5B-Instruct` and the default multilingual embedding model is `paraphrase-multilingual-MiniLM-L12-v2`.

## Testing

Run the database tests with:

```bash
pytest -q
```

## Roadmap

- Streaming responses
- Authentication and API keys
- Better document chunking and reranking
- Optional web-research provider
- LoRA fine-tuning pipeline
- Evaluation benchmarks
- Optional vector database backend
- Web dashboard

## License

See `LICENSE`.
