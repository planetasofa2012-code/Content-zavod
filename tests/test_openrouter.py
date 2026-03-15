"""Тесты для ai/openrouter.py — мокируем HTTP-запросы."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai.openrouter import chat, generate_text


def _make_mock_client(response_content: str = "Тестовый ответ"):
    """Создаёт мок httpx.AsyncClient с заданным ответом."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": response_content}}]
    }

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def _make_error_client(error: Exception):
    """Создаёт мок клиент, который бросает исключение."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=error)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


# === chat ===

@pytest.mark.asyncio
async def test_chat_returns_content():
    mock_client = _make_mock_client("Привет от AI!")
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await chat([{"role": "user", "content": "Привет"}])
    assert result == "Привет от AI!"


@pytest.mark.asyncio
async def test_chat_passes_messages_to_api():
    mock_client = _make_mock_client("Ок")
    with patch("httpx.AsyncClient", return_value=mock_client):
        await chat([{"role": "user", "content": "Тест"}], model="test-model")

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
    assert payload["messages"][0]["content"] == "Тест"
    assert payload["model"] == "test-model"


@pytest.mark.asyncio
async def test_chat_fallback_to_reserve_model_on_error():
    """При ошибке основной модели — используется резервная."""
    call_count = 0

    async def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Основная модель недоступна")
        # Второй вызов (резервная модель) — успех
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Резервный ответ"}}]
        }
        return mock_response

    mock_client = AsyncMock()
    mock_client.post = mock_post
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await chat(
            [{"role": "user", "content": "Тест"}],
            model="google/gemini-2.0-flash-001",
        )
    assert result == "Резервный ответ"
    assert call_count == 2


@pytest.mark.asyncio
async def test_chat_raises_when_reserve_also_fails():
    """Если и резервная упала — поднимаем исключение наверх."""
    mock_client = _make_error_client(Exception("Все модели недоступны"))
    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(Exception):
            await chat(
                [{"role": "user", "content": "Тест"}],
                model="anthropic/claude-3-haiku-20240307",  # Уже резервная
            )


@pytest.mark.asyncio
async def test_chat_respects_temperature_and_max_tokens():
    mock_client = _make_mock_client("Ок")
    with patch("httpx.AsyncClient", return_value=mock_client):
        await chat(
            [{"role": "user", "content": "Тест"}],
            temperature=0.1,
            max_tokens=100,
        )
    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
    assert payload["temperature"] == 0.1
    assert payload["max_tokens"] == 100


# === generate_text ===

@pytest.mark.asyncio
async def test_generate_text_returns_string():
    mock_client = _make_mock_client("Сгенерированный текст")
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await generate_text("Напиши что-нибудь")
    assert result == "Сгенерированный текст"


@pytest.mark.asyncio
async def test_generate_text_with_system_prompt():
    mock_client = _make_mock_client("Ок")
    with patch("httpx.AsyncClient", return_value=mock_client):
        await generate_text("Промпт", system_prompt="Системный промпт")

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
    messages = payload["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "Системный промпт"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Промпт"


@pytest.mark.asyncio
async def test_generate_text_without_system_prompt():
    mock_client = _make_mock_client("Ок")
    with patch("httpx.AsyncClient", return_value=mock_client):
        await generate_text("Только юзер")

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
    messages = payload["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
