"""Тесты для ai/knowledge_base.py"""
import json
import pytest
import ai.knowledge_base as kb_module


@pytest.fixture(autouse=True)
def use_tmp_kb(tmp_path, monkeypatch):
    """Каждый тест использует свой временный файл базы знаний."""
    monkeypatch.setattr(kb_module, "KB_FILE", tmp_path / "kb.json")


# === load_knowledge_base ===

def test_load_empty_when_file_missing():
    result = kb_module.load_knowledge_base()
    assert result == []


def test_load_empty_list_from_empty_array(tmp_path, monkeypatch):
    kb_file = tmp_path / "kb.json"
    kb_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(kb_module, "KB_FILE", kb_file)
    assert kb_module.load_knowledge_base() == []


def test_load_invalid_json_returns_empty(tmp_path, monkeypatch):
    kb_file = tmp_path / "kb.json"
    kb_file.write_text("not valid json {{{{", encoding="utf-8")
    monkeypatch.setattr(kb_module, "KB_FILE", kb_file)
    assert kb_module.load_knowledge_base() == []


# === save_to_knowledge_base ===

def test_save_returns_correct_count():
    count = kb_module.save_to_knowledge_base("Вопрос?", "Ответ!", "test")
    assert count == 1


def test_save_increments_count_on_each_call():
    kb_module.save_to_knowledge_base("Q1", "A1", "cat")
    count = kb_module.save_to_knowledge_base("Q2", "A2", "cat")
    assert count == 2


def test_save_persists_all_fields():
    kb_module.save_to_knowledge_base("Сколько стоит?", "От 150 тыс", "prices")
    kb = kb_module.load_knowledge_base()
    assert len(kb) == 1
    entry = kb[0]
    assert entry["question"] == "Сколько стоит?"
    assert entry["answer"] == "От 150 тыс"
    assert entry["category"] == "prices"
    assert "date" in entry


def test_save_increments_id_sequentially():
    kb_module.save_to_knowledge_base("Q1", "A1", "c1")
    kb_module.save_to_knowledge_base("Q2", "A2", "c2")
    kb_module.save_to_knowledge_base("Q3", "A3", "c3")
    kb = kb_module.load_knowledge_base()
    assert [e["id"] for e in kb] == [1, 2, 3]


def test_save_without_category():
    kb_module.save_to_knowledge_base("Вопрос?", "Ответ!")
    kb = kb_module.load_knowledge_base()
    assert kb[0]["category"] == ""


# === get_knowledge_for_agent ===

def test_get_knowledge_empty_returns_placeholder():
    result = kb_module.get_knowledge_for_agent()
    assert result == "База знаний пока пуста."


def test_get_knowledge_formats_correctly():
    kb_module.save_to_knowledge_base("Сколько?", "Дорого", "prices")
    result = kb_module.get_knowledge_for_agent()
    assert "Вопрос: Сколько?" in result
    assert "Ответ: Дорого" in result
    assert "---" in result


def test_get_knowledge_includes_all_entries():
    kb_module.save_to_knowledge_base("Q1", "A1", "c1")
    kb_module.save_to_knowledge_base("Q2", "A2", "c2")
    result = kb_module.get_knowledge_for_agent()
    assert "Q1" in result
    assert "Q2" in result
    assert "A1" in result
    assert "A2" in result
