"""
Тесты для утилитарных функций в обработчиках.
Тестируем чистую логику без запуска Telegram-бота.
"""
import pytest

# Импортируем напрямую из модулей
from bot.content_bot.handlers import _extract_section, safe_send
from bot.agent_bot.handlers import _should_suggest_booking


# === _extract_section ===

SAMPLE_POST = """=== TELEGRAM ===
Красивая кухня! Заходите в гости.

=== ВКОНТАКТЕ ===
Подробный пост ВКонтакте с описанием и хештегами.
#кухня #мебель

=== INSTAGRAM ===
Инстаграм пост здесь.

=== PINTEREST ===
Заголовок Pinterest | описание для SEO"""


def test_extract_section_telegram():
    result = _extract_section(SAMPLE_POST, "TELEGRAM")
    assert "Красивая кухня" in result
    assert "ВКОНТАКТЕ" not in result


def test_extract_section_vk():
    result = _extract_section(SAMPLE_POST, "ВКОНТАКТЕ")
    assert "Подробный пост ВКонтакте" in result
    assert "#кухня" in result
    assert "INSTAGRAM" not in result


def test_extract_section_instagram():
    result = _extract_section(SAMPLE_POST, "INSTAGRAM")
    assert "Инстаграм пост" in result
    assert "PINTEREST" not in result


def test_extract_section_pinterest():
    result = _extract_section(SAMPLE_POST, "PINTEREST")
    assert "Заголовок Pinterest" in result


def test_extract_section_missing_marker_returns_fallback():
    text = "Просто текст без маркеров " * 20
    result = _extract_section(text, "TELEGRAM")
    # Fallback: первые 500 символов
    assert len(result) <= 500


def test_extract_section_unknown_section_returns_fallback():
    result = _extract_section(SAMPLE_POST, "НЕСУЩЕСТВУЮЩАЯ")
    assert len(result) <= 500


def test_extract_section_strips_whitespace():
    result = _extract_section(SAMPLE_POST, "TELEGRAM")
    assert result == result.strip()


# === safe_send ===

def test_safe_send_short_text_unchanged():
    text = "Короткий текст"
    assert safe_send(text) == text


def test_safe_send_long_text_truncated():
    text = "А" * 5000
    result = safe_send(text)
    assert len(result) <= 4003  # 4000 + "..."
    assert result.endswith("...")


def test_safe_send_exactly_at_limit():
    text = "Б" * 4000
    result = safe_send(text)
    assert result == text
    assert not result.endswith("...")


def test_safe_send_one_over_limit():
    text = "В" * 4001
    result = safe_send(text)
    assert result.endswith("...")
    assert len(result) == 4003


def test_safe_send_custom_max_len():
    text = "Г" * 200
    result = safe_send(text, max_len=100)
    assert len(result) == 103  # 100 + "..."
    assert result.endswith("...")


# === _should_suggest_booking ===

def test_should_suggest_booking_keyword_замер():
    assert _should_suggest_booking("Давайте организуем замер на удобное время") is True


def test_should_suggest_booking_keyword_бесплатн():
    assert _should_suggest_booking("Предлагаем бесплатную консультацию") is True


def test_should_suggest_booking_keyword_приехать():
    assert _should_suggest_booking("Мастер может приехать к вам домой") is True


def test_should_suggest_booking_keyword_записать():
    assert _should_suggest_booking("Хотите записаться на замер?") is True


def test_should_suggest_booking_no_keywords():
    assert _should_suggest_booking("МДФ эмаль — отличный материал для кухни") is False


def test_should_suggest_booking_empty_string():
    assert _should_suggest_booking("") is False


def test_should_suggest_booking_case_insensitive():
    assert _should_suggest_booking("ЗАМЕР бесплатный!") is True
