import sqlite3
from pathlib import Path

class Database:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._init()

    def connect(self):
        return sqlite3.connect(self.path)

    def _init(self):
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                source TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            db.execute("""CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    def add_memory(self, text, source="user"):
        with self.connect() as db:
            cur = db.execute("INSERT INTO memories(text, source) VALUES (?, ?)", (text, source))
            return int(cur.lastrowid)

    def get_memories(self):
        with self.connect() as db:
            return db.execute("SELECT id,text,source,created_at FROM memories ORDER BY id DESC").fetchall()

    def add_message(self, role, content):
        with self.connect() as db:
            db.execute("INSERT INTO messages(role,content) VALUES (?,?)", (role, content))

    def recent_messages(self, limit=10):
        with self.connect() as db:
            rows = db.execute("SELECT role,content FROM messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return list(reversed(rows))
