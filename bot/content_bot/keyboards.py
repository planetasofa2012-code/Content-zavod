"""
Inline-клавиатуры контент-бота.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню контент-бота."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Создать пост", callback_data="create_post")],
        [InlineKeyboardButton(text="🎙️ Интервью", callback_data="interview")],
        [InlineKeyboardButton(text="💡 Идея", callback_data="idea")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
    ])


def post_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа поста."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📸 Портфолио", callback_data="type_portfolio"),
            InlineKeyboardButton(text="📝 Кейс", callback_data="type_case"),
        ],
        [
            InlineKeyboardButton(text="💡 Совет", callback_data="type_tip"),
            InlineKeyboardButton(text="⭐ Отзыв", callback_data="type_review"),
        ],
        [
            InlineKeyboardButton(text="🔥 Акция", callback_data="type_promo"),
        ],
    ])


def preview_keyboard() -> InlineKeyboardMarkup:
    """Кнопки предпросмотра поста."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish"),
            InlineKeyboardButton(text="✏️ Переделать", callback_data="regenerate"),
        ],
        [
            InlineKeyboardButton(text="🖼️ Генерировать картинку", callback_data="gen_image"),
        ],
        [
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel"),
        ],
    ])


def confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение действия."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no"),
        ],
    ])


def image_result_keyboard() -> InlineKeyboardMarkup:
    """Кнопки после генерации картинок."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ещё 3 варианта", callback_data="gen_image")],
        [InlineKeyboardButton(text="◀️ Назад к посту", callback_data="back_to_post")],
    ])


def interview_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню AI-интервьюера."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Начать интервью (3-5 вопросов)", callback_data="interview_full")],
        [InlineKeyboardButton(text="💬 Случайный вопрос", callback_data="interview_random")],
        [InlineKeyboardButton(text="📱 Переслать переписку", callback_data="interview_forward")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")],
    ])


def interview_after_answer_keyboard() -> InlineKeyboardMarkup:
    """Кнопки после сохранения ответа в базу знаний."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Следующий вопрос", callback_data="interview_random")],
        [InlineKeyboardButton(text="📝 Сделать пост из ответа", callback_data="interview_to_post")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_main")],
    ])
