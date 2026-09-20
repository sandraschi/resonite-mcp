"""Unit tests for spawn_registry (file-backed, tmp_path isolated)."""

from resonite_mcp.spawn_registry import list_entries, record, remove


def test_record_and_list_newest_first(tmp_path):
    db = tmp_path / "spawns.json"
    assert list_entries(db) == []
    first = record("room", "RoomA", slot_id="Reso_1", detail="3/3", path=db)
    second = record("model", "Chair", slot_id="Reso_2", path=db)
    assert first["id"] != second["id"]
    assert first["created_at"] and second["created_at"]
    listed = list_entries(db)
    assert [e["id"] for e in listed] == [second["id"], first["id"]]


def test_remove(tmp_path):
    db = tmp_path / "spawns.json"
    entry = record("room", "RoomA", slot_id="Reso_1", path=db)
    assert remove("nope", db) is None
    removed = remove(entry["id"], db)
    assert removed is not None and removed["id"] == entry["id"]
    assert list_entries(db) == []


def test_corrupt_file_reads_empty(tmp_path):
    db = tmp_path / "spawns.json"
    db.write_text("not json{", encoding="utf-8")
    assert list_entries(db) == []
    # recording repairs the file
    record("room", "RoomB", path=db)
    assert len(list_entries(db)) == 1
