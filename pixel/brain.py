from .config import settings
from .database import Database
from .memory import Memory
from .model import PixelModel

SYSTEM_PROMPT = """You are PIXEL, a modular local AI assistant.

Rules:
- Be helpful, clear, practical, and honest.
- Use memory as context, not as unquestionable truth.
- Never invent a fact just because it sounds plausible.
- If the supplied context is insufficient, say that you do not know.
- Answer in the user's language unless asked otherwise.
- Do not claim that model weights changed when information was only stored in memory.
"""


class PixelBrain:
    def __init__(self):
        self.db = Database(settings.db_path)
        self.memory = Memory(
            self.db,
            settings.embedding_model,
            settings.max_memory_results,
            settings.memory_threshold,
            settings.memory_duplicate_threshold,
        )
        self.model = PixelModel(settings.model_name, settings.max_new_tokens)

    def learn(self, text: str, source: str = "user", category: str = "general", importance: int = 3) -> dict:
        return self.memory.add(text, source, category, importance)

    def forget(self, memory_id: int) -> dict:
        return {"status": "deleted" if self.memory.forget(memory_id) else "not_found", "id": memory_id}

    def memories(self, limit: int = 50) -> list[dict]:
        return self.memory.list(limit)

    def search(self, query: str, limit: int | None = None) -> list[dict]:
        return self.memory.search(query, limit)

    def clear_chat(self, session_id: str = "default") -> dict:
        return {"deleted_messages": self.db.clear_messages(session_id), "session_id": session_id}

    def ask(self, user_text: str, session_id: str = "default", temperature: float = 0.7) -> dict:
        user_text = user_text.strip()
        if not user_text:
            raise ValueError("Message cannot be empty.")
        memories = self.memory.search(user_text)
        memory_context = "\n".join(
            f"- [{item['category']}] {item['text']} (relevance={item['score']:.2f})" for item in memories
        ) or "No relevant memory was found."
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Relevant PIXEL memory:\n{memory_context}"},
        ]
        messages.extend(
            {"role": role, "content": content}
            for role, content in self.db.recent_messages(session_id, settings.max_history_messages)
        )
        messages.append({"role": "user", "content": user_text})
        answer = self.model.generate(messages, temperature=temperature)
        self.db.add_message(session_id, "user", user_text)
        self.db.add_message(session_id, "assistant", answer)
        return {"answer": answer, "memory_used": memories, "session_id": session_id, "model": self.model.info()}

    def health(self) -> dict:
        return {"status": "ok", "version": "2.0.0", "model": self.model.info(), "memory_count": len(self.memory.texts)}
