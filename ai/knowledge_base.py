"""
База знаний — хранилище ответов Александра.
Каждый ответ сохраняется с вопросом, категорией и датой.
Используется AI-агентом для консультаций клиентов.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Файл базы знаний (рядом с проектом)
KB_FILE = Path(__file__).parent.parent / "knowledge_base.json"


def load_knowledge_base() -> list[dict]:
    """Загрузить базу знаний."""
    if not KB_FILE.exists():
        return []
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки базы знаний: {e}")
        return []


def save_to_knowledge_base(question: str, answer: str, category: str = "") -> int:
    """Сохранить ответ в базу знаний. Возвращает общее количество записей."""
    kb = load_knowledge_base()

    entry = {
        "id": len(kb) + 1,
        "question": question,
        "answer": answer,
        "category": category,
        "date": datetime.now().isoformat(),
    }
    kb.append(entry)

    try:
        with open(KB_FILE, "w", encoding="utf-8") as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 База знаний: сохранена запись #{entry['id']} ({category})")
    except Exception as e:
        logger.error(f"Ошибка сохранения в базу знаний: {e}")

    return len(kb)


def get_knowledge_for_agent() -> str:
    """Получить текст базы знаний для промпта AI-агента."""
    kb = load_knowledge_base()
    if not kb:
        return "База знаний пока пуста."

    lines = []
    for entry in kb:
        lines.append(f"Вопрос: {entry['question']}")
        lines.append(f"Ответ: {entry['answer']}")
        lines.append("---")

    return "\n".join(lines)
