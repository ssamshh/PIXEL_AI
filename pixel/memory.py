import numpy as np
from sentence_transformers import SentenceTransformer

class Memory:
    def __init__(self, db, embedding_model, max_results=5):
        self.db = db
        self.max_results = max_results
        self.encoder = SentenceTransformer(embedding_model)
        self.ids, self.texts, self.vectors = [], [], []
        self._load()

    def _load(self):
        for memory_id, text, _, _ in self.db.get_memories():
            self.ids.append(memory_id)
            self.texts.append(text)
        if self.texts:
            self.vectors = self.encoder.encode(self.texts, normalize_embeddings=True, show_progress_bar=False)

    def add(self, text, source="user"):
        memory_id = self.db.add_memory(text, source)
        vector = self.encoder.encode([text], normalize_embeddings=True)[0]
        self.ids.append(memory_id)
        self.texts.append(text)
        self.vectors = np.array([vector]) if len(self.vectors) == 0 else np.vstack([self.vectors, vector])

    def search(self, query):
        if not self.texts:
            return []
        q = self.encoder.encode([query], normalize_embeddings=True)[0]
        scores = np.dot(self.vectors, q)
        order = np.argsort(scores)[::-1][:self.max_results]
        return [{"text": self.texts[i], "score": float(scores[i])} for i in order if float(scores[i]) > 0.25]
