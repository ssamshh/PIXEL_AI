# PIXEL AI 3.0

PIXEL is a local-first assistant with a browser workspace, SQLite conversation history, editable persistent memory, safe arithmetic tools, optional local Transformers inference, web search, document extraction, optional vision endpoint support, browser voice, and a local Python plugin loader.

> **Honest capability note:** no software can be guaranteed “bug-free.” This release includes tests and explicit fallbacks, but you should run the tests on your machine. The default Qwen model is text-only. Vision requires a separately configured vision-capable OpenAI-compatible endpoint. Web search requires the optional `ddgs` package and internet access. PDF/DOCX support requires optional document packages. The browser voice features depend on browser support.

## Quick start (Ubuntu/Linux)

```bash
unzip PIXEL-AI-v3.0.zip
cd PIXEL-AI-v3.0
bash scripts/install.sh
source .venv/bin/activate
uvicorn pixel.api:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/app**. API docs: **http://127.0.0.1:8000/docs**.

Install optional features as needed:

```bash
pip install -e '.[ai]'                 # local Transformers model
pip install -e '.[memory]'             # sentence-transformers (optional semantic memory backend groundwork)
pip install -e '.[documents]'          # PDF and DOCX extraction
pip install -e '.[search]'              # DDGS web search
pip install -e '.[dev]'                # tests
pip install -e '.[ai,documents,search,dev]'
```

The API and UI can start without downloading model weights. The first model-backed chat may download the model and require substantial disk space/RAM; CPU generation may be slow. Copy `.env.example` to `.env` and customize settings.

## Features

- **Core brain/model:** lazy local Hugging Face Transformers loading; graceful error response if optional dependencies or weights are unavailable.
- **Memory 3.0:** persistent SQLite memory, category, importance, add/edit/delete, keyword retrieval and use-count schema fields. The default retriever is lightweight lexical matching and does not require a model download.
- **Sessions:** multiple persistent sessions and message history stored in SQLite.
- **Tool system:** registered tools, orchestrator and conservative router. Calculator parses Python AST and never uses `eval`.
- **Web search:** optional DDGS provider; source URLs/snippets are shown in the UI.
- **File intelligence:** text extraction for TXT/MD/CSV/JSON/PY/LOG; PDF and DOCX when optional dependencies are installed; 12 MB upload limit.
- **Vision:** sends images to a configured OpenAI-compatible vision endpoint; it does not pretend the default text-only Qwen model understands images.
- **Streaming API:** `/chat/stream` uses server-sent events. The current local Transformers backend generates a complete answer before emitting text chunks; true token-by-token model streaming is a future optimization.
- **Web GUI:** chat, sessions, memory manager, calculator, web search, file reader, vision, dashboard, theme switch and responsive layout.
- **Voice:** browser speech recognition and speech synthesis where supported.
- **Plugin system:** discovers trusted Python files in `plugins/` exporting a `plugin` object. Plugins execute code with the app's privileges; inspect every plugin before adding it.
- **REST API:** FastAPI and interactive `/docs`.
- **Tests and scripts:** pytest suite and Linux installer/start scripts.

## Configuration

Copy `.env.example` to `.env`. Important values:

| Variable | Purpose |
|---|---|
| `PIXEL_MODEL` | Hugging Face text model ID |
| `PIXEL_DB` | SQLite database path |
| `PIXEL_MAX_NEW_TOKENS` | Maximum generated tokens |
| `PIXEL_MAX_HISTORY_MESSAGES` | Conversation context size |
| `PIXEL_WEB_SEARCH_ENABLED` | Enable/disable web search |
| `PIXEL_VISION_API_URL` | Base URL of an OpenAI-compatible vision API |
| `PIXEL_VISION_API_KEY` | Optional private API key |
| `PIXEL_VISION_MODEL` | Vision-capable model identifier |
| `PIXEL_HOST`, `PIXEL_PORT` | Bind address and port |

Do not commit `.env` or API keys. The default host is `127.0.0.1`, so the service is not exposed to your LAN by default.

## API

- `GET /health`, `GET /api/settings`, `GET /dashboard`
- `POST /chat`, `POST /chat/stream`
- `GET /sessions`, `GET /chat/history?session_id=default`
- `DELETE /sessions/{session_id}`, `DELETE /chat/{session_id}`
- `POST /learn`, `GET /memory`, `GET /memory/search?q=...`
- `PATCH /memory/{id}`, `DELETE /memory/{id}`
- `GET /tools`, `POST /tools/run`, `POST /search`
- `POST /files/read`, `POST /vision`, `GET /plugins`

## Tests

```bash
source .venv/bin/activate
python -m pytest -q\npython -m pixel.cli
```

## Project layout

```text
pixel/
  api.py
  core/brain.py
  database.py
  memory.py
  model.py
  documents.py
  vision.py
  plugins.py
  tools/{base,calculator,registry,router,orchestrator,search}.py
web/{index.html,style.css,app.js}
plugins/
scripts/
tests/
data/knowledge/
```

## Security and limitations

- This is a personal local app, not a multi-user production service. It has no login or API authentication. Keep it bound to localhost and do not expose it publicly without adding authentication, CSRF protections, rate limits and deployment hardening.
- Python plugins are arbitrary code. Only load plugins you trust.
- Search/vision services may send queries or images to external providers; check their privacy terms.
- The default memory retrieval is lexical rather than vector-semantic. It is dependable offline but less nuanced than an embedding-based retriever.
- Streaming currently streams chunks after generation finishes, not during model decoding.
- The test suite covers core behavior, not every browser, model, provider, or operating system.

## License

See `LICENSE`.
