"""Тесты для publishers/"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# === telegram_pub ===

@pytest.mark.asyncio
async def test_telegram_raises_when_no_channel_id(monkeypatch):
    import publishers.telegram_pub as tg_module
    monkeypatch.setattr(tg_module, "TG_CHANNEL_ID", "")

    mock_bot = AsyncMock()
    with pytest.raises(ValueError, match="TG_CHANNEL_ID"):
        await tg_module.publish_to_telegram(mock_bot, "file_id", "Текст поста")


@pytest.mark.asyncio
async def test_telegram_publishes_successfully(monkeypatch):
    import publishers.telegram_pub as tg_module
    monkeypatch.setattr(tg_module, "TG_CHANNEL_ID", "-1001234567890")

    mock_bot = AsyncMock()
    mock_bot.send_photo = AsyncMock()

    result = await tg_module.publish_to_telegram(mock_bot, "file_id_123", "Текст поста")

    assert result is True
    mock_bot.send_photo.assert_called_once()
    call_kwargs = mock_bot.send_photo.call_args.kwargs
    assert call_kwargs["chat_id"] == "-1001234567890"
    assert call_kwargs["photo"] == "file_id_123"
    assert call_kwargs["caption"] == "Текст поста"
    assert call_kwargs["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_telegram_truncates_long_caption(monkeypatch):
    import publishers.telegram_pub as tg_module
    monkeypatch.setattr(tg_module, "TG_CHANNEL_ID", "-100123")

    mock_bot = AsyncMock()
    mock_bot.send_photo = AsyncMock()

    long_text = "А" * 2000
    await tg_module.publish_to_telegram(mock_bot, "file_id", long_text)

    sent_caption = mock_bot.send_photo.call_args.kwargs["caption"]
    assert len(sent_caption) <= 1024
    assert sent_caption.endswith("...")


@pytest.mark.asyncio
async def test_telegram_does_not_truncate_short_caption(monkeypatch):
    import publishers.telegram_pub as tg_module
    monkeypatch.setattr(tg_module, "TG_CHANNEL_ID", "-100123")

    mock_bot = AsyncMock()
    mock_bot.send_photo = AsyncMock()

    short_text = "Короткий текст поста"
    await tg_module.publish_to_telegram(mock_bot, "file_id", short_text)

    sent_caption = mock_bot.send_photo.call_args.kwargs["caption"]
    assert sent_caption == short_text


@pytest.mark.asyncio
async def test_telegram_raises_on_bot_error(monkeypatch):
    import publishers.telegram_pub as tg_module
    monkeypatch.setattr(tg_module, "TG_CHANNEL_ID", "-100123")

    mock_bot = AsyncMock()
    mock_bot.send_photo = AsyncMock(side_effect=Exception("Bot API error"))

    with pytest.raises(Exception, match="Bot API error"):
        await tg_module.publish_to_telegram(mock_bot, "file_id", "Текст")


# === vk_pub ===

def test_vk_check_response_ok():
    from publishers.vk_pub import _check_vk_response

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"response": {"post_id": 42}}

    result = _check_vk_response(mock_resp, "wall.post")
    assert result["response"]["post_id"] == 42


def test_vk_check_response_raises_on_vk_error():
    from publishers.vk_pub import _check_vk_response

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "error": {"error_code": 5, "error_msg": "User authorization failed"}
    }

    with pytest.raises(Exception, match="VK API error"):
        _check_vk_response(mock_resp, "photos.getWallUploadServer")


def test_vk_check_response_raises_on_http_error():
    from publishers.vk_pub import _check_vk_response
    import httpx

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "403 Forbidden", request=MagicMock(), response=MagicMock()
    )

    with pytest.raises(httpx.HTTPStatusError):
        _check_vk_response(mock_resp, "test_step")


@pytest.mark.asyncio
async def test_vk_raises_when_no_credentials(monkeypatch):
    import publishers.vk_pub as vk_module
    monkeypatch.setattr(vk_module, "VK_GROUP_TOKEN", "")
    monkeypatch.setattr(vk_module, "VK_GROUP_ID", 0)

    with pytest.raises(ValueError, match="VK_GROUP_TOKEN"):
        await vk_module.publish_to_vk(b"photo_data", "Текст поста")
