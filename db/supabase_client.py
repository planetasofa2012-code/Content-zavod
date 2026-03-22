"""
Supabase-клиент для Python-бота.
Создаёт лидов, сохраняет посты и знания в БД → автоматически появляются в CRM.
"""

import os
import logging
from datetime import datetime
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# Supabase REST API
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


async def _request(method: str, table: str, data: dict = None, params: dict = None) -> dict | list | None:
    """Универсальный запрос к Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase не настроен — пропускаю запрос")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if method == "POST":
                resp = await client.post(url, json=data, headers=HEADERS)
            elif method == "PATCH":
                resp = await client.patch(url, json=data, headers=HEADERS, params=params)
            elif method == "GET":
                resp = await client.get(url, headers=HEADERS, params=params)
            else:
                return None
            
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Supabase {method} {table} ошибка: {e}")
        return None


# ====================
# CRM: Лиды
# ====================

async def create_lead(
    name: str,
    phone: str = "",
    type: str = "kitchen",
    source: str = "telegram",
    description: str = "",
    budget: int = 0,
    priority: str = "medium",
    telegram_id: int = None,
    telegram_username: str = "",
) -> Optional[dict]:
    """Создать нового лида в CRM. Вызывается когда клиент начинает диалог с ботом."""
    data = {
        "name": name,
        "phone": phone,
        "type": type,
        "source": source,
        "description": description,
        "budget": budget,
        "status": "lead",
        "priority": priority,
        "notes": "",
    }
    
    # Сохраняем Telegram-инфо в notes (JSON-like)
    if telegram_id:
        data["notes"] = f"tg_id:{telegram_id}"
        if telegram_username:
            data["notes"] += f", tg_user:@{telegram_username}"
    
    result = await _request("POST", "leads", data)
    if result:
        logger.info(f"✅ Лид создан в CRM: {name} ({source})")
    return result[0] if isinstance(result, list) and result else result


async def update_lead_status(lead_id: str, status: str) -> Optional[dict]:
    """Обновить статус лида (lead → measurement → project → ...)."""
    result = await _request("PATCH", "leads", {"status": status}, {"id": f"eq.{lead_id}"})
    return result


async def find_lead_by_telegram(telegram_id: int) -> Optional[dict]:
    """Найти лида по Telegram ID (хранится в notes)."""
    result = await _request("GET", "leads", params={
        "notes": f"like.*tg_id:{telegram_id}*",
        "order": "created_at.desc",
        "limit": "1",
    })
    return result[0] if isinstance(result, list) and result else None


# ====================
# Контент: Посты
# ====================

async def save_post(
    title: str,
    content: str,
    platforms: list[str] = None,
    status: str = "draft",
    ai_generated: bool = True,
    image_url: str = None,
) -> Optional[dict]:
    """Сохранить пост в БД. Вызывается после генерации через контент-бота."""
    data = {
        "title": title,
        "content": content,
        "platforms": platforms or ["telegram"],
        "status": status,
        "ai_generated": ai_generated,
        "stats": {"views": 0, "likes": 0, "comments": 0},
    }
    if image_url:
        data["image_url"] = image_url
    if status == "published":
        data["published_at"] = datetime.utcnow().isoformat()
    
    result = await _request("POST", "posts", data)
    if result:
        logger.info(f"✅ Пост сохранён: {title[:50]}")
    return result[0] if isinstance(result, list) and result else result


async def update_post_status(post_id: str, status: str) -> Optional[dict]:
    """Обновить статус поста (draft → published)."""
    data = {"status": status}
    if status == "published":
        data["published_at"] = datetime.utcnow().isoformat()
    result = await _request("PATCH", "posts", data, {"id": f"eq.{post_id}"})
    return result


# ====================
# База знаний
# ====================

async def save_knowledge(
    question: str,
    answer: str,
    category: str = "faq",
    source: str = "interview",
) -> Optional[dict]:
    """Сохранить Q&A в базу знаний Supabase (параллельно с JSON-файлом)."""
    data = {
        "question": question,
        "answer": answer,
        "category": category,
        "source": source,
    }
    result = await _request("POST", "knowledge_entries", data)
    if result:
        logger.info(f"✅ Знание сохранено: {question[:50]}")
    return result[0] if isinstance(result, list) and result else result


# ====================
# Статистика
# ====================

async def track_event(event_type: str, data: dict = None):
    """Простой трекинг событий (для будущей аналитики)."""
    logger.info(f"📊 Event: {event_type} | {data}")
    # TODO: Сохранять в daily_stats или отдельную таблицу events
