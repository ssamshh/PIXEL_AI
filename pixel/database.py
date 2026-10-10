import json
import sqlite3
from pathlib import Path
from typing import Any

class Database:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init(self):
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS memories(
                id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL,
                source TEXT DEFAULT 'user', category TEXT DEFAULT 'general',
                importance INTEGER DEFAULT 3, embedding TEXT,
                use_count INTEGER NOT NULL DEFAULT 0,
                last_used_at TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            db.execute("""CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL DEFAULT 'default',
                role TEXT NOT NULL, content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            db.execute("""CREATE TABLE IF NOT EXISTS sessions(
                id TEXT PRIMARY KEY, title TEXT NOT NULL DEFAULT 'New chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            self._add_column(db, "memories", "category", "TEXT DEFAULT 'general'")
            self._add_column(db, "memories", "importance", "INTEGER DEFAULT 3")
            self._add_column(db, "memories", "embedding", "TEXT")
            self._add_column(db, "memories", "use_count", "INTEGER NOT NULL DEFAULT 0")
            self._add_column(db, "memories", "last_used_at", "TEXT")
            self._add_column(db, "messages", "session_id", "TEXT NOT NULL DEFAULT 'default'")
            db.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id,id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
            db.execute("INSERT OR IGNORE INTO sessions(id,title) VALUES('default','Chat')")

    @staticmethod
    def _add_column(db, table, column, definition):
        cols = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
        if column not in cols:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def add_memory(self, text, source="user", category="general", importance=3):
        with self.connect() as db:
            cur = db.execute("INSERT INTO memories(text,source,category,importance) VALUES(?,?,?,?)",
                             (text, source, category, max(1,min(5,int(importance)))))
            return cur.lastrowid

    def list_memories(self, limit=100):
        with self.connect() as db:
            rows = db.execute("SELECT id,text,source,category,importance,use_count,last_used_at,created_at FROM memories ORDER BY importance DESC,id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(x) for x in rows]

    def get_memory(self, memory_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
        return dict(row) if row else None

    def update_memory(self, memory_id, text=None, category=None, importance=None):
        fields, values = [], []
        for key, val in (("text",text),("category",category),("importance",importance)):
            if val is not None:
                fields.append(f"{key}=?"); values.append(max(1,min(5,int(val))) if key=="importance" else val)
        if not fields: return False
        values.append(memory_id)
        with self.connect() as db:
            cur = db.execute(f"UPDATE memories SET {','.join(fields)} WHERE id=?", values)
        return cur.rowcount > 0

    def delete_memory(self, memory_id):
        with self.connect() as db:
            cur = db.execute("DELETE FROM memories WHERE id=?", (memory_id,))
        return cur.rowcount > 0

    def search_memories(self, query, limit=5):
        terms = {w.lower() for w in query.split() if len(w)>1}
        items = self.list_memories(1000)
        scored = []
        for item in items:
            words = {w.lower() for w in item["text"].split()}
            score = len(terms & words) / max(1, len(terms))
            if score > 0:
                scored.append((score + item["importance"]*0.005, item))
        scored.sort(key=lambda x:x[0], reverse=True)
        results=[]
        for score,item in scored[:limit]:
            item = dict(item); item["score"] = round(score,3); results.append(item)
        return results

    def add_message(self, session_id, role, content):
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO sessions(id,title) VALUES(?,?)",
                       (session_id, content[:45] if role=="user" else "New chat"))
            db.execute("UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (session_id,))
            cur=db.execute("INSERT INTO messages(session_id,role,content) VALUES(?,?,?)",(session_id,role,content))
            return cur.lastrowid

    def recent_messages(self, session_id="default", limit=16):
        with self.connect() as db:
            rows=db.execute("SELECT role,content FROM (SELECT id,role,content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?) ORDER BY id",(session_id,limit)).fetchall()
        return [(r["role"],r["content"]) for r in rows]

    def list_sessions(self):
        with self.connect() as db:
            rows=db.execute("""SELECT s.id,s.title,s.created_at,s.updated_at,
                (SELECT COUNT(*) FROM messages m WHERE m.session_id=s.id) AS message_count
                FROM sessions s ORDER BY s.updated_at DESC""").fetchall()
        return [dict(r) for r in rows]

    def delete_session(self, session_id):
        if session_id == "default": self.clear_messages(session_id); return True
        with self.connect() as db:
            db.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
            cur=db.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        return cur.rowcount > 0

    def clear_messages(self, session_id="default"):
        with self.connect() as db:
            cur=db.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
        return cur.rowcount
