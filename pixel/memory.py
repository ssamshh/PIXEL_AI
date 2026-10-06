import numpy as np
from sentence_transformers import SentenceTransformer


class Memory:
    def __init__(self, db, embedding_model: str, max_results: int = 5,
                 threshold: float = 0.25, duplicate_threshold: float = 0.94):
        self.db = db
        self.max_results = max_results
        self.threshold = threshold
        self.duplicate_threshold = duplicate_threshold
        self.encoder = SentenceTransformer(embedding_model)
        self.ids: list[int] = []
        self.texts: list[str] = []
        self.vectors = np.empty((0, 0), dtype=np.float32)
        self._load()

    def _load(self) -> None:
        memories = self.db.get_memories()
        missing: list[dict] = []
        vectors: list[np.ndarray] = []
        for item in memories:
            self.ids.append(item["id"])
            self.texts.append(item["text"])
            if item.get("embedding"):
                vectors.append(np.asarray(item["embedding"], dtype=np.float32))
            else:
                missing.append(item)
        if missing:
            new_vectors = self.encoder.encode(
                [item["text"] for item in missing], normalize_embeddings=True, show_progress_bar=False
            )
            for item, vector in zip(missing, new_vectors):
                self.db.update_memory(item["id"], embedding=vector.tolist())
                # Replace by ID below so ordering remains stable.
        by_id = {item["id"]: item for item in memories}
        for item in missing:
            by_id[item["id"]]["embedding"] = self.db.get_memory(item["id"])["embedding"]
        ordered = [by_id[memory_id]["embedding"] for memory_id in self.ids]
        if ordered:
            self.vectors = np.asarray(ordered, dtype=np.float32)

    def _encode(self, text: str) -> np.ndarray:
        return np.asarray(
            self.encoder.encode([text], normalize_embeddings=True, show_progress_bar=False)[0],
            dtype=np.float32,
        )

    def add(self, text: str, source: str = "user", category: str = "general", importance: int = 3) -> dict:
        text = text.strip()
        if not text:
            raise ValueError("Memory cannot be empty.")
        vector = self._encode(text)
        if self.vectors.size:
            score = float(np.max(np.dot(self.vectors, vector)))
            if score >= self.duplicate_threshold:
                index = int(np.argmax(np.dot(self.vectors, vector)))
                return {"status": "duplicate", "id": self.ids[index], "score": score, "text": self.texts[index]}
        memory_id = self.db.add_memory(text, source, category, max(1, min(5, importance)), vector.tolist())
        self.ids.append(memory_id)
        self.texts.append(text)
        self.vectors = vector.reshape(1, -1) if self.vectors.size == 0 else np.vstack([self.vectors, vector])
        return {"status": "stored", "id": memory_id, "text": text, "category": category, "importance": importance}

    def search(self, query: str, limit: int | None = None) -> list[dict]:
        if not self.texts:
            return []
        vector = self._encode(query)
        scores = np.dot(self.vectors, vector)
        order = np.argsort(scores)[::-1]
        limit = limit or self.max_results
        results = []
        for index in order:
            score = float(scores[index])
            if score < self.threshold:
                continue
            item = self.db.get_memory(self.ids[int(index)])
            if item:
                item.pop("embedding", None)
                item["score"] = score
                results.append(item)
            if len(results) >= limit:
                break
        return results

    def list(self, limit: int = 50) -> list[dict]:
        items = self.db.get_memories(limit)
        for item in items:
            item.pop("embedding", None)
        return items

    def forget(self, memory_id: int) -> bool:
        deleted = self.db.delete_memory(memory_id)
        if not deleted:
            return False
        index = self.ids.index(memory_id)
        self.ids.pop(index)
        self.texts.pop(index)
        if self.vectors.size:
            self.vectors = np.delete(self.vectors, index, axis=0)
        return True
