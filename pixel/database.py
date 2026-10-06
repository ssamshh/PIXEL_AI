import json
import sqlite3
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def _init(self) -> None:
        with self.connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    source TEXT DEFAULT 'user',
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 3,
                    embedding TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT DEFAULT 'default',
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._add_column(db, "memories", "category", "TEXT DEFAULT 'general'")
            self._add_column(db, "memories", "importance", "INTEGER DEFAULT 3")
            self._add_column(db, "memories", "embedding", "TEXT")
            self._add_column(db, "messages", "session_id", "TEXT DEFAULT 'default'")
            db.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")

    @staticmethod
    def _add_column(db: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def add_memory(self, text: str, source: str, category: str, importance: int, embedding: list[float] | None) -> int:
        encoded = json.dumps(embedding) if embedding is not None else None
        with self.connect() as db:
            cur = db.execute(
                "INSERT INTO memories(text, source, category, importance, embedding) VALUES (?, ?, ?, ?, ?)",
                (text, source, category, importance, encoded),
            )
            return int(cur.lastrowid)

    def update_memory(self, memory_id: int, **fields: Any) -> bool:
        allowed = {"text", "source", "category", "importance", "embedding"}
        fields = {key: value for key, value in fields.items() if key in allowed}
        if not fields:
            return False
        if "embedding" in fields and fields["embedding"] is not None:
            fields["embedding"] = json.dumps(fields["embedding"])
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [memory_id]
        with self.connect() as db:
            cur = db.execute(f"UPDATE memories SET {assignments} WHERE id = ?", values)
            return cur.rowcount > 0

    def delete_memory(self, memory_id: int) -> bool:
        with self.connect() as db:
            cur = db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            return cur.rowcount > 0

    def get_memory(self, memory_id: int) -> dict | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
        return self._memory_row(row) if row else None

    def get_memories(self, limit: int | None = None) -> list[dict]:
        sql = "SELECT * FROM memories ORDER BY id DESC"
        params: tuple = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)
        with self.connect() as db:
            rows = db.execute(sql, params).fetchall()
        return [self._memory_row(row) for row in rows]

    @staticmethod
    def _memory_row(row: sqlite3.Row) -> dict:
        item = dict(row)
        raw = item.get("embedding")
        item["embedding"] = json.loads(raw) if raw else None
        return item

    def add_message(self, session_id: str, role: str, content: str) -> int:
        with self.connect() as db:
            cur = db.execute(
                "INSERT INTO messages(session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )
            return int(cur.lastrowid)

    def recent_messages(self, session_id: str = "default", limit: int = 12) -> list[tuple[str, str]]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [(row[0], row[1]) for row in reversed(rows)]

    def clear_messages(self, session_id: str = "default") -> int:
        with self.connect() as db:
            cur = db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            return cur.rowcount
