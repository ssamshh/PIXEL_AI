# PIXEL AI 3.5

PIXEL is a modular, local-first AI assistant with a browser workspace, persistent SQLite memory and conversations, a safe calculator, optional web search, document extraction and Q&A, configurable model backends, optional vision endpoint support, and local Python plugins.

> **Capability note:** tests cover core behavior, not every model/provider/browser. The local model backend needs optional Transformers dependencies and downloads model weights on first use. The OpenAI-compatible backend needs a reachable compatible endpoint (for example, a local Ollama server configured for its OpenAI-compatible API, or a hosted service). Web search requires `ddgs` and internet access. PDF/DOCX extraction needs optional document packages. Vision requires a separately configured vision-capable endpoint. Voice uses browser support.

## Quick start (Ubuntu/Linux)

```bash
unzip PIXEL-AI-v3.5.zip
cd PIXEL-AI-v3.5
bash scripts/install.sh
source .venv/bin/activate
uvicorn pixel.api:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/app**. API docs: **http://127.0.0.1:8000/docs**.

The installer installs the lightweight API and test dependencies. Add optional capabilities when needed:

```bash
pip install -e '.[ai]'                 # local Transformers model
pip install -e '.[documents]'          # PDF and DOCX extraction
pip install -e '.[search]'             # DDGS web search
pip install -e '.[dev]'                # test tools
pip install -e '.[ai,documents,search,dev]'
```

## What's new in 3.5

- **Multiple model backends:** choose local Transformers or an OpenAI-compatible `/chat/completions` endpoint. The API key is read from `.env` and never returned by settings endpoints.
- **Conversation improvements:** session history endpoint, persistent sessions, and session renaming API.
- **Document Q&A:** upload a supported text/PDF/DOCX file and ask a question about its extracted text through `POST /files/ask`. Document text is treated as untrusted context, not system instructions.
- **Memory usage tracking:** retrieved memories increment their usage count and last-used timestamp.
- **Safer release packaging:** no personal SQLite database is bundled; a fresh database is created on first run.
- Preserves the v3 browser UI, memory CRUD, calculator, web search, vision adapter, plugin discovery, and optional browser voice.

## Features

- **Memory:** persistent SQLite memory with category, importance, duplicate checks, edit/delete, keyword retrieval and usage metadata. Retrieval is lexical by default; this release does not claim semantic vector retrieval.
- **Sessions:** separate persistent histories, list/delete/clear, history retrieval and rename endpoint.
- **Tools:** registered tools, deterministic arithmetic routing, calculator based on AST parsing (never `eval`).
- **Web search:** optional DDGS provider; search is a separate explicit action and may fail if the provider/network is unavailable.
- **Files:** TXT, MD, CSV, JSON, PY, LOG, PDF and DOCX text extraction, plus document Q&A. Upload limit is 12 MB.
- **Vision:** configured OpenAI-compatible vision endpoint; the default local Qwen text model is not treated as vision-capable.
- **Browser workspace:** chat, sessions, memory manager, calculator, web search, file reader, vision, dashboard, theme switch, responsive layout, Markdown/code presentation and browser voice where supported.
- **Streaming endpoint:** `POST /chat/stream` emits server-sent events. The current backends produce a complete model answer before the API emits text chunks; this is chunked delivery, not true token-by-token model decoding.
- **Plugins:** discovers trusted Python files in `plugins/` exporting a `plugin` object. Python plugins run with application privileges; inspect them before use.
- **REST API:** FastAPI and interactive `/docs`.
- **Tests and scripts:** pytest suite and Linux install/run scripts.

## Model configuration

Copy `.env.example` to `.env` and edit it. Default is the optional local Transformers backend. To use an OpenAI-compatible server, set:

```dotenv
PIXEL_MODEL_PROVIDER=openai
PIXEL_MODEL=your-model-name
PIXEL_API_BASE_URL=http://127.0.0.1:11434/v1
PIXEL_API_KEY=
PIXEL_REQUEST_TIMEOUT=90
```

Use the base URL expected by your provider; PIXEL appends `/chat/completions`. For hosted providers, keep your API key private and never commit `.env`. The default host is `127.0.0.1`, so the app is not exposed to the LAN by default.

## API endpoints

- `GET /health`, `GET /api/settings`, `GET /dashboard`
- `POST /chat`, `POST /chat/stream`
- `GET /sessions`, `PATCH /sessions/{session_id}`, `DELETE /sessions/{session_id}`
- `GET /chat/history?session_id=default`, `DELETE /chat/{session_id}`
- `POST /learn`, `GET /memory`, `GET /memory/search?q=...`, `PATCH /memory/{id}`, `DELETE /memory/{id}`
- `GET /tools`, `POST /tools/run`, `POST /search`
- `POST /files/read`, `POST /files/ask`, `POST /vision`, `GET /plugins`

## Tests

```bash
source .venv/bin/activate
python -m pytest -q
```

## Security and limitations

- This is a personal local app, not a multi-user production service. It has no login/API authentication. Keep it bound to localhost and do not expose it publicly without authentication, CSRF protections, rate limits and deployment hardening.
- Python plugins are arbitrary code. Only load plugins you trust.
- Search/vision/model requests can send data to external providers depending on configuration. Review provider privacy terms.
- Memory retrieval is lexical and can miss paraphrases. Streaming is chunked after generation completes. The tests do not guarantee every environment is error-free.

## License

See `LICENSE`.
