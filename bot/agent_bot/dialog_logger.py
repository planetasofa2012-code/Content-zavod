"""
Логирование диалогов AI-агента.
Сохраняет все сообщения клиентов и ответы бота в JSON-файлы.
Каждый клиент = отдельный файл. При /start начинается новая сессия.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Папка для логов диалогов
LOGS_DIR = Path(__file__).parent.parent.parent / "logs" / "dialogs"


def _ensure_dir():
    """Создаёт папку для логов если не существует."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _get_log_path(user_id: int) -> Path:
    """Путь к файлу лога для конкретного пользователя."""
    return LOGS_DIR / f"user_{user_id}.json"


def _load_log(user_id: int) -> dict:
    """Загрузить лог пользователя."""
    path = _get_log_path(user_id)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"user_id": user_id, "sessions": []}
    return {"user_id": user_id, "sessions": []}


def _save_log(user_id: int, data: dict):
    """Сохранить лог пользователя."""
    _ensure_dir()
    path = _get_log_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def start_session(user_id: int, username: str = "", full_name: str = "", source: str = ""):
    """Начать новую сессию диалога (при /start)."""
    log = _load_log(user_id)

    session = {
        "session_id": len(log["sessions"]) + 1,
        "started_at": datetime.now().isoformat(),
        "user_info": {
            "username": username,
            "full_name": full_name,
            "source": source,
        },
        "messages": [],
        "summary": None,  # Заполняется при анализе
    }

    log["sessions"].append(session)
    log["username"] = username
    log["full_name"] = full_name
    _save_log(user_id, log)

    logger.info(f"[DialogLog] Новая сессия #{session['session_id']} для user_{user_id} ({full_name})")


def log_message(user_id: int, role: str, content: str, message_type: str = "text"):
    """
    Записать сообщение в лог.
    role: 'user' или 'assistant'
    message_type: 'text', 'photo', 'document', 'voice'
    """
    log = _load_log(user_id)

    if not log["sessions"]:
        # Сессия не начата — начинаем автоматически
        start_session(user_id)
        log = _load_log(user_id)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content,
        "type": message_type,
    }

    log["sessions"][-1]["messages"].append(entry)
    _save_log(user_id, log)


def get_all_sessions(user_id: int) -> list:
    """Получить все сессии пользователя."""
    log = _load_log(user_id)
    return log.get("sessions", [])


def get_all_users() -> list[dict]:
    """Получить список всех пользователей с количеством сессий."""
    _ensure_dir()
    users = []
    for file in LOGS_DIR.glob("user_*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            users.append({
                "user_id": data.get("user_id"),
                "username": data.get("username", ""),
                "full_name": data.get("full_name", ""),
                "sessions_count": len(data.get("sessions", [])),
                "total_messages": sum(
                    len(s.get("messages", [])) for s in data.get("sessions", [])
                ),
            })
        except (json.JSONDecodeError, IOError):
            continue
    return users


def export_for_analysis() -> str:
    """
    Экспортировать все диалоги в читаемый формат для анализа.
    Возвращает текст со всеми диалогами.
    """
    _ensure_dir()
    output = []
    output.append("=" * 60)
    output.append("АНАЛИЗ ДИАЛОГОВ AI-АГЕНТА")
    output.append(f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    output.append("=" * 60)

    for file in sorted(LOGS_DIR.glob("user_*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        user_id = data.get("user_id", "?")
        full_name = data.get("full_name", "Неизвестно")
        username = data.get("username", "")

        for session in data.get("sessions", []):
            output.append(f"\n{'─' * 60}")
            output.append(f"Клиент: {full_name} (@{username}) [ID: {user_id}]")
            output.append(f"Сессия #{session.get('session_id', '?')}")
            output.append(f"Начало: {session.get('started_at', '?')}")
            output.append(f"Сообщений: {len(session.get('messages', []))}")
            output.append(f"{'─' * 60}")

            for msg in session.get("messages", []):
                role = "🧑 Клиент" if msg["role"] == "user" else "🤖 Аня"
                time = msg.get("timestamp", "")[:19].replace("T", " ")
                msg_type = f" [{msg['type']}]" if msg.get("type") != "text" else ""
                output.append(f"{time} {role}{msg_type}:")
                output.append(f"  {msg['content'][:500]}")
                output.append("")

    return "\n".join(output)
