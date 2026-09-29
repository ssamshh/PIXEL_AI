from .config import settings
from .database import Database
from .memory import Memory
from .model import PixelModel

SYSTEM_PROMPT = """You are PIXEL, a helpful modular AI assistant.

Rules:
- Be clear, useful, and honest.
- Use supplied memory as context, not as unquestionable truth.
- If memory is insufficient, say so instead of inventing facts.
- Never claim to have permanently learned something unless it was stored.
- Answer in the user's language.
- Keep answers practical and structured.
"""

class PixelBrain:
    def __init__(self):
        self.db = Database(settings.db_path)
        self.memory = Memory(self.db, settings.embedding_model, settings.max_memory_results)
        self.model = PixelModel(settings.model_name, settings.max_new_tokens)

    def learn(self, text, source="user"):
        text = text.strip()
        if not text:
            raise ValueError("Knowledge cannot be empty.")
        self.memory.add(text, source)
        return {"status": "stored", "text": text}

    def ask(self, user_text):
        user_text = user_text.strip()
        if not user_text:
            raise ValueError("Message cannot be empty.")
        memories = self.memory.search(user_text)
        context = "\n".join(f"- {x['text']}" for x in memories) or "No relevant memory was found."
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Relevant PIXEL memory:\n{context}"},
        ]
        for role, content in self.db.recent_messages(10):
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_text})
        answer = self.model.generate(messages)
        self.db.add_message("user", user_text)
        self.db.add_message("assistant", answer)
        return {"answer": answer, "memory_used": memories}
