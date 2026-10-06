from pixel.database import Database


def test_memory_and_messages(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    memory_id = db.add_memory("hello", "test", "general", 3, [1.0, 0.0])
    assert db.get_memory(memory_id)["text"] == "hello"
    assert db.update_memory(memory_id, category="test")
    assert db.get_memory(memory_id)["category"] == "test"
    db.add_message("s1", "user", "hi")
    assert db.recent_messages("s1") == [("user", "hi")]
    assert db.delete_memory(memory_id)
