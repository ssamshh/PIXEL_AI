from pixel.database import Database
from pixel.core.brain import PixelBrain

class FakeModel:
    def info(self):
        return {"provider": "test", "model": "fake", "available": True}
    def generate(self, messages, temperature=0.7):
        assert any("document context" in m["content"] for m in messages if m["role"] == "system")
        return "Document answer"

def test_session_history_and_rename(tmp_path):
    db = Database(str(tmp_path / "db.sqlite"))
    db.add_message("session-a", "user", "Hello")
    assert db.rename_session("session-a", "My project")
    assert next(s for s in db.list_sessions() if s["id"] == "session-a")["title"] == "My project"
    assert db.session_history("session-a")[0]["content"] == "Hello"

def test_memory_usage_is_tracked(tmp_path):
    db = Database(str(tmp_path / "db.sqlite"))
    mid = db.add_memory("I am learning Python", category="study", importance=4)
    found = db.search_memories("Python", 1)
    assert found and found[0]["id"] == mid
    assert db.get_memory(mid)["use_count"] == 1

def test_document_context_reaches_model(tmp_path):
    brain = PixelBrain(db_path=str(tmp_path / "db.sqlite"), model=FakeModel())
    result = brain.ask("Summarize this", session_id="doc-test", use_tools=False, extra_context="document context: sample")
    assert result["answer"] == "Document answer"
