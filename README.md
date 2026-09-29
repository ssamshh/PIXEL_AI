# 🧠 PIXEL AI

### A Modular Deep Learning AI Assistant with Semantic Memory, RAG, Local LLM Inference and an Extensible Architecture

**PIXEL** is a modular Deep Learning AI assistant designed to combine a local language model with semantic memory, Retrieval-Augmented Generation (RAG), persistent conversation history, knowledge ingestion, and an API interface.

The main idea behind PIXEL is simple:

> **Give PIXEL knowledge, let it remember that knowledge, retrieve the relevant information when needed, and use a Deep Learning language model to generate the final response.**

PIXEL is designed as a foundation that can grow into a much larger AI system with future support for vision, speech, tools, agents, fine-tuning, web interfaces, and other AI capabilities.

---

## ✨ Features

### 🧠 Deep Learning Language Model

PIXEL uses a local language model through:

* PyTorch
* Hugging Face Transformers
* AutoTokenizer
* AutoModelForCausalLM

The default model configuration is:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

The model name can be changed through environment variables, allowing PIXEL to work with other compatible Hugging Face causal language models.

---

### 💾 Persistent Long-Term Memory

PIXEL has a persistent memory system based on SQLite.

When PIXEL learns new information, it stores the information in a local database instead of keeping it only in RAM.

For example:

```text
/learn PIXEL is an AI project focused on Deep Learning.
```

The information is stored and can later be retrieved when a related question is asked.

Memory survives program restarts because it is stored in:

```text
data/pixel.db
```

---

### 🔎 Semantic Memory Search

PIXEL does not only search for exact words.

It converts memories into vector embeddings using:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

When a user asks a question:

1. The question is converted into an embedding.
2. PIXEL compares it with stored memory vectors.
3. The most semantically relevant memories are selected.
4. The selected memories are given to the language model as context.

This allows PIXEL to find related information even when the wording is different.

---

### 📚 RAG — Retrieval-Augmented Generation

PIXEL uses a lightweight RAG architecture.

The process is approximately:

```text
User Question
      │
      ▼
Create Query Embedding
      │
      ▼
Search Semantic Memory
      │
      ▼
Retrieve Relevant Knowledge
      │
      ▼
Build Model Context
      │
      ▼
Deep Learning Language Model
      │
      ▼
Generated Answer
```

This means PIXEL does not need to modify the model's weights every time new information is added.

Instead, new knowledge can be stored and retrieved dynamically.

---

## 🧩 How PIXEL Works

The main architecture can be represented as:

```text
                    ┌─────────────────┐
                    │      USER       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PIXEL BRAIN   │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
       Conversation       Semantic        Language
          History          Memory           Model
             │               │               │
             ▼               ▼               ▼
          SQLite       Embeddings        Transformers
                             │
                             ▼
                         RAG Context
                             │
                             └───────┐
                                     ▼
                              Final Response
```

The central component is:

```text
PixelBrain
```

It connects:

* Database
* Memory
* Embedding model
* Language model
* Conversation history
* User input

---

# 📁 Project Structure

```text
PIXEL-AI/
│
├── pixel/
│   ├── __init__.py
│   ├── api.py
│   ├── brain.py
│   ├── cli.py
│   ├── config.py
│   ├── database.py
│   ├── memory.py
│   └── model.py
│
├── scripts/
│   ├── ingest.py
│   └── prepare_dataset.py
│
├── data/
│   ├── knowledge/
│   └── training_examples.example.jsonl
│
├── models/
│
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

# 🔬 Core Components

## `pixel/brain.py`

This is the main orchestration layer of PIXEL.

The `PixelBrain` class connects the major components together:

```python
class PixelBrain:
    def __init__(self):
        self.db = Database(...)
        self.memory = Memory(...)
        self.model = PixelModel(...)
```

When PIXEL receives a question, the process is:

```text
Question
   ↓
Validate input
   ↓
Search memory
   ↓
Retrieve relevant information
   ↓
Load recent conversation
   ↓
Build messages
   ↓
Send to language model
   ↓
Generate answer
   ↓
Save conversation
   ↓
Return response
```

This makes `PixelBrain` the central controller of the system.

---

# 🤖 `pixel/model.py`

This file handles the Deep Learning language model.

PIXEL uses:

```python
AutoTokenizer
AutoModelForCausalLM
```

from Hugging Face Transformers.

The model automatically detects whether CUDA is available:

```python
self.device = "cuda" if torch.cuda.is_available() else "cpu"
```

Therefore PIXEL can run on:

* NVIDIA GPU with CUDA
* CPU-only systems

GPU execution is significantly more practical for larger models.

---

## Text Generation

PIXEL generates responses using parameters such as:

```text
temperature = 0.7
top_p = 0.9
repetition_penalty = 1.05
```

These parameters control aspects of generation such as randomness, token selection, and repetition.

The maximum number of generated tokens is configurable through:

```text
PIXEL_MAX_NEW_TOKENS
```

---

# 🧠 `pixel/memory.py`

This module implements PIXEL's semantic memory.

It uses:

```text
Sentence Transformers
```

to convert text into numerical vectors.

For example:

```text
"RoboCup is a robot soccer competition."
```

becomes an embedding vector.

PIXEL can then compare this vector with other stored memories.

---

## Similarity Search

PIXEL uses normalized embeddings and vector similarity:

```python
scores = np.dot(self.vectors, q)
```

The highest-scoring memories are selected.

The default maximum number of retrieved memories is:

```text
5
```

This can be configured using:

```text
PIXEL_MAX_MEMORY_RESULTS
```

PIXEL also uses a similarity threshold so that weakly related memories are ignored.

---

# 💾 `pixel/database.py`

SQLite is used for persistent storage.

PIXEL currently stores two main types of information.

### Memories

```text
id
text
source
created_at
```

### Messages

```text
id
role
content
created_at
```

This allows PIXEL to maintain:

* Long-term knowledge
* Conversation history
* Source information
* Timestamps

No external database server is required.

---

# ⚙️ `pixel/config.py`

Configuration is centralized in one place.

PIXEL supports environment variables such as:

```text
PIXEL_MODEL
PIXEL_EMBEDDING_MODEL
PIXEL_DB
PIXEL_MAX_MEMORY_RESULTS
PIXEL_MAX_NEW_TOKENS
```

Example:

```env
PIXEL_MODEL=Qwen/Qwen2.5-0.5B-Instruct
PIXEL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
PIXEL_DB=data/pixel.db
PIXEL_MAX_MEMORY_RESULTS=5
PIXEL_MAX_NEW_TOKENS=256
```

This makes it possible to change the model and configuration without modifying the source code.

---

# 💬 CLI Interface

PIXEL includes a simple terminal interface.

Start it with:

```bash
python -m pixel.cli
```

You can then chat with PIXEL:

```text
You: Hello PIXEL
PIXEL: Hello! How can I help you?
```

---

## Teaching PIXEL New Information

PIXEL supports a simple learning command:

```text
/learn TEXT
```

Example:

```text
/learn PIXEL is a modular Deep Learning AI project.
```

PIXEL stores this information in its persistent semantic memory.

Later:

```text
You: What is PIXEL?
```

The stored information can be retrieved and supplied to the language model.

---

# 🌐 FastAPI Interface

PIXEL also exposes a REST API using FastAPI.

Run:

```bash
uvicorn pixel.api:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides interactive API documentation.

---

## Available Endpoints

### `GET /`

Returns basic PIXEL information.

Example:

```json
{
  "name": "PIXEL",
  "status": "online"
}
```

---

### `GET /health`

Health check endpoint.

Example:

```json
{
  "status": "ok"
}
```

---

### `POST /chat`

Send a message to PIXEL.

Example request:

```json
{
  "message": "What is Deep Learning?"
}
```

PIXEL returns the generated answer and information about the memories used.

---

### `POST /learn`

Add knowledge to PIXEL.

Example:

```json
{
  "text": "PIXEL is a modular AI assistant.",
  "source": "manual"
}
```

The information is stored in semantic memory.

---

# 📚 Knowledge Ingestion

PIXEL can import knowledge from files.

Supported formats:

```text
.txt
.md
.json
.csv
```

Place knowledge files inside:

```text
data/knowledge/
```

Then run:

```bash
python scripts/ingest.py
```

The ingestion script:

1. Finds supported files.
2. Reads their contents.
3. Splits large files into smaller chunks.
4. Sends each chunk to PIXEL memory.
5. Creates embeddings.
6. Stores the knowledge.

This provides a simple way to give PIXEL a large knowledge base.

---

# 🧪 Training Dataset

PIXEL also includes the foundation for creating a custom training dataset.

Example:

```json
{"instruction":"What is PIXEL?","output":"PIXEL is a modular Deep Learning AI assistant."}
```

Training examples can be prepared using:

```bash
python scripts/prepare_dataset.py
```

The prepared dataset uses a conversational format:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is PIXEL?"
    },
    {
      "role": "assistant",
      "content": "PIXEL is a modular Deep Learning AI assistant."
    }
  ]
}
```

This format can later be used as the foundation for supervised fine-tuning.

---

# 🧠 Memory Learning vs Model Training

One of the most important concepts in PIXEL is the difference between **memory** and **training**.

## Memory Learning

When you use:

```text
/learn ...
```

PIXEL does **not** change the neural network weights.

Instead:

```text
New Information
      ↓
Embedding
      ↓
Database
      ↓
Semantic Search
      ↓
Retrieved During Chat
```

This is fast and practical for continuously adding knowledge.

---

## Fine-Tuning

Fine-tuning is different.

During fine-tuning:

```text
Training Dataset
       ↓
Deep Learning Model
       ↓
Gradient Updates
       ↓
Updated Weights / Adapter
```

This can change how the model behaves.

PIXEL's current architecture prepares for this direction, while the included version focuses primarily on memory-based learning and RAG.

---

# 🚀 Installation

## Requirements

Recommended:

```text
Python 3.10+
8 GB+ RAM
NVIDIA GPU + CUDA (optional)
```

CPU execution is supported, but larger language models can require significant memory and computation time.

---

## Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/PIXEL-AI.git
cd PIXEL-AI
```

---

## Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Main dependencies include:

```text
PyTorch
Transformers
Accelerate
Sentence Transformers
FastAPI
Uvicorn
Pydantic
python-dotenv
NumPy
PEFT
Datasets
```

---

# ▶️ Running PIXEL

## Terminal Mode

```bash
python -m pixel.cli
```

---

## API Mode

```bash
uvicorn pixel.api:app --host 0.0.0.0 --port 8000
```

Then visit:

```text
http://127.0.0.1:8000/docs
```

---

# 🔐 Configuration

Copy:

```bash
cp .env.example .env
```

Then customize the configuration.

For example:

```env
PIXEL_MODEL=Qwen/Qwen2.5-0.5B-Instruct
PIXEL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
PIXEL_DB=data/pixel.db
PIXEL_MAX_MEMORY_RESULTS=5
PIXEL_MAX_NEW_TOKENS=256
```

---

# 🧱 Design Philosophy

PIXEL is designed around several principles.

### 1. Modular

Each major part has its own module.

```text
Model
Memory
Database
Brain
API
CLI
```

This makes future development easier.

---

### 2. Local First

The starter configuration runs the language model locally through Hugging Face and PyTorch.

This reduces dependence on external AI APIs for the core generation pipeline.

---

### 3. Persistent Knowledge

PIXEL's memory is stored locally rather than being lost after the program exits.

---

### 4. Extensible

The architecture is intended to support additional modules without rewriting the entire project.

---

### 5. Separation of Memory and Model

New knowledge is stored separately from the model weights.

This makes continuous knowledge updates much easier and safer than retraining the model after every new piece of information.

---

# 🛠️ Future Development Roadmap

PIXEL is intended to evolve beyond a text-only assistant.

## Phase 1 — Current Foundation

* [x] Local language model
* [x] Deep Learning inference
* [x] Semantic memory
* [x] SQLite persistence
* [x] RAG
* [x] Conversation history
* [x] Knowledge ingestion
* [x] CLI
* [x] FastAPI
* [x] Dataset preparation

---

## Phase 2 — Advanced Learning

Planned:

* [ ] LoRA fine-tuning
* [ ] PEFT training pipeline
* [ ] Training configuration system
* [ ] Dataset validation
* [ ] Evaluation system
* [ ] Model checkpoint management
* [ ] Training dashboard

---

## Phase 3 — Vision

Planned:

```text
PIXEL Vision
```

Potential capabilities:

* Image understanding
* Object recognition
* Image classification
* OCR
* Visual question answering
* Image analysis

---

## Phase 4 — Voice

Planned:

```text
PIXEL Voice
```

Potential capabilities:

* Speech-to-text
* Text-to-speech
* Voice conversations
* Wake-word support
* Multilingual voice interaction

---

## Phase 5 — AI Agents

PIXEL can eventually evolve into an agent capable of using external tools.

Potential architecture:

```text
                 PIXEL
                   │
            ┌──────┴──────┐
            │             │
         Reasoning      Memory
            │             │
            └──────┬──────┘
                   │
                Tool Router
                   │
       ┌───────────┼───────────┐
       │           │           │
     Files        Web        Code
       │           │           │
       └───────────┼───────────┘
                   │
                Result
                   │
                   ▼
              PIXEL Response
```

Potential tools could include:

* File operations
* Web search
* Code execution
* Data analysis
* APIs
* Databases
* Robotics interfaces

---

# 🖥️ Future Web Interface

A future version can provide a complete web application:

```text
┌───────────────────────────────────────────┐
│                 PIXEL AI                  │
├───────────────────────────────────────────┤
│                                           │
│  Conversation                             │
│                                           │
│  User: Explain neural networks            │
│                                           │
│  PIXEL: A neural network is...            │
│                                           │
├───────────────────────────────────────────┤
│  Type your message...              [Send] │
└───────────────────────────────────────────┘
```

Possible technologies:

* React
* Vite
* Tailwind CSS
* FastAPI
* WebSockets

---

# 🌍 Multilingual Support

PIXEL is designed to work with multilingual text.

The default embedding model is multilingual, making semantic memory suitable for languages beyond English.

For example:

```text
User:
هوش مصنوعی چیست؟

PIXEL:
...
```

or:

```text
User:
What is artificial intelligence?

PIXEL:
...
```

The system prompt also instructs PIXEL to answer in the user's language.

---

# ⚡ Performance

Performance depends heavily on:

* Model size
* CPU/GPU
* Available RAM/VRAM
* Number of memories
* Input length
* Generated token count

GPU acceleration is automatically used when CUDA is available.

For larger models, significantly more VRAM/RAM may be required.

---

# 🔒 Security and Privacy

PIXEL is designed to run locally, but users should still protect sensitive data.

Do **not** commit:

```text
.env
API keys
passwords
private documents
personal secrets
database files
model weights
```

The repository's `.gitignore` excludes sensitive and generated files.

---

# ⚠️ Current Limitations

PIXEL is a foundation for a larger AI system, not a finished general-purpose AGI.

The current version does **not** automatically provide:

* Human-level reasoning
* Guaranteed factual accuracy
* Automatic web browsing
* Computer control
* Vision
* Speech
* Autonomous agents
* Full model fine-tuning
* Perfect memory management

The quality of responses depends on the selected language model and available hardware.

---

# 🧪 Example Workflow

A simple PIXEL workflow looks like this:

```text
1. Start PIXEL
       ↓
2. Give PIXEL knowledge
       ↓
3. Knowledge becomes embeddings
       ↓
4. Embeddings are stored in SQLite
       ↓
5. Ask a question
       ↓
6. PIXEL searches semantic memory
       ↓
7. Relevant memories are retrieved
       ↓
8. Conversation context is added
       ↓
9. Language model generates response
       ↓
10. Conversation is saved
```

---

# 🧑‍💻 Development

The project is intentionally separated into independent modules.

For example, changing the language model primarily involves configuration rather than rewriting the entire application.

This allows developers to experiment with:

* Different LLMs
* Different embedding models
* Different databases
* Different APIs
* Different memory strategies
* Different user interfaces

---

# 📜 License

PIXEL is released under the MIT License.

See:

```text
LICENSE
```

for the complete license text.

---

# ⭐ Contributing

Contributions are welcome.

Possible areas include:

* Better memory systems
* New model integrations
* Fine-tuning
* Vision
* Speech
* Agent systems
* UI development
* Performance optimization
* Testing
* Documentation

A typical workflow:

```bash
git clone https://github.com/YOUR_USERNAME/PIXEL-AI.git
cd PIXEL-AI

git checkout -b feature/my-feature

# Make your changes

git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

---

# 🚀 Vision

PIXEL is intended to become more than a simple chatbot.

The long-term goal is to build a modular AI platform where:

```text
                 ┌───────────────────┐
                 │       PIXEL       │
                 └─────────┬─────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
   Language             Vision              Voice
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                      PIXEL BRAIN
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Memory         Tools        Learning
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                       Web / API
```

The current repository provides the foundation for that architecture.

---

## 📌 Project Status

**Status:** Early Development / Experimental

PIXEL currently provides a working foundation for:

* Local Deep Learning inference
* Semantic memory
* RAG
* Persistent storage
* Knowledge ingestion
* CLI interaction
* REST API

The architecture is intentionally designed to be expanded into a larger AI system over time.

---

# 🧠 PIXEL

**Learn. Remember. Retrieve. Generate. Evolve.**
