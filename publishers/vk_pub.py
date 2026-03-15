"""
Публикатор: VK-группа.
Отправляет пост с фото в группу «Разговоры на кухне».
"""

import logging
import httpx
from bot.config import VK_GROUP_TOKEN, VK_GROUP_ID

logger = logging.getLogger(__name__)

VK_API_URL = "https://api.vk.com/method"
VK_API_VERSION = "5.199"


def _check_vk_response(resp: httpx.Response, step: str) -> dict:
    """Проверяет HTTP-статус и VK error в ответе."""
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        err = data["error"]
        raise Exception(f"VK API error at {step}: [{err.get('error_code')}] {err.get('error_msg')}")
    return data


async def publish_to_vk(photo_data: bytes, text: str) -> bool:
    """Публикует пост с фото в VK-группу."""
    if not VK_GROUP_TOKEN or not VK_GROUP_ID:
        raise ValueError("VK_GROUP_TOKEN или VK_GROUP_ID не настроены в .env")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # 1. Получить URL для загрузки фото
            upload_url_resp = await client.get(
                f"{VK_API_URL}/photos.getWallUploadServer",
                params={
                    "access_token": VK_GROUP_TOKEN,
                    "group_id": VK_GROUP_ID,
                    "v": VK_API_VERSION,
                },
            )
            upload_url_data = _check_vk_response(upload_url_resp, "getWallUploadServer")
            upload_url = upload_url_data["response"]["upload_url"]

            # 2. Загрузить фото
            upload_resp = await client.post(
                upload_url,
                files={"photo": ("photo.jpg", photo_data, "image/jpeg")},
            )
            upload_resp.raise_for_status()
            upload_result = upload_resp.json()

            # 3. Сохранить фото
            save_resp = await client.get(
                f"{VK_API_URL}/photos.saveWallPhoto",
                params={
                    "access_token": VK_GROUP_TOKEN,
                    "group_id": VK_GROUP_ID,
                    "photo": upload_result["photo"],
                    "server": upload_result["server"],
                    "hash": upload_result["hash"],
                    "v": VK_API_VERSION,
                },
            )
            save_data = _check_vk_response(save_resp, "saveWallPhoto")
            photo_info = save_data["response"][0]
            attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}"

            # 4. Создать пост на стене
            wall_resp = await client.get(
                f"{VK_API_URL}/wall.post",
                params={
                    "access_token": VK_GROUP_TOKEN,
                    "owner_id": f"-{VK_GROUP_ID}",
                    "from_group": 1,
                    "message": text,
                    "attachments": attachment,
                    "v": VK_API_VERSION,
                },
            )
            wall_data = _check_vk_response(wall_resp, "wall.post")

            post_id = wall_data["response"]["post_id"]
            logger.info(f"Опубликовано в VK: post_id={post_id}")
            return True

    except Exception as e:
        logger.error(f"Ошибка публикации в VK: {e}")
        raise
