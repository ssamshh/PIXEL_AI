from pixel.database import Database
from pixel.memory import MemoryManager

def test_database_memory_and_sessions(tmp_path):
    db=Database(str(tmp_path/"pixel.db"))
    memory=MemoryManager(db)
    saved=memory.add("I like Python",category="preference",importance=4)
    assert saved["status"]=="stored"
    assert memory.list()[0]["text"]=="I like Python"
    assert memory.update(saved["id"],text="I enjoy Python",importance=5)
    assert memory.list()[0]["text"]=="I enjoy Python"
    db.add_message("test-session","user","Hello")
    assert db.recent_messages("test-session")==[("user","Hello")]
    assert db.list_sessions()
    assert memory.forget(saved["id"])
