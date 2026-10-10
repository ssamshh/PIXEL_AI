from .database import Database

class MemoryManager:
    """Persistent memory with a lightweight lexical search fallback (no embedding download required)."""
    def __init__(self, db: Database):
        self.db = db

    def add(self, text, source="user", category="general", importance=3):
        text = text.strip()
        if not text: raise ValueError("Memory cannot be empty.")
        existing = self.db.search_memories(text, 1)
        if existing and existing[0]["score"] >= 0.95:
            return {"status":"duplicate","id":existing[0]["id"],"text":existing[0]["text"]}
        memory_id = self.db.add_memory(text, source, category, importance)
        return {"status":"stored","id":memory_id,"text":text,"category":category,"importance":max(1,min(5,int(importance)))}

    def list(self, limit=100): return self.db.list_memories(limit)
    def search(self, query, limit=5): return self.db.search_memories(query, limit)
    def update(self, memory_id, text=None, category=None, importance=None):
        return self.db.update_memory(memory_id,text,category,importance)
    def forget(self, memory_id): return self.db.delete_memory(memory_id)
