"""
Inline-клавиатуры AI-агента для клиентов.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def welcome_keyboard() -> InlineKeyboardMarkup:
    """Приветственная клавиатура — что ищет клиент."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽 Кухню", callback_data="want_kitchen"),
            InlineKeyboardButton(text="🚪 Шкаф", callback_data="want_wardrobe"),
        ],
        [
            InlineKeyboardButton(text="👗 Гардеробную", callback_data="want_closet"),
            InlineKeyboardButton(text="❓ Другое", callback_data="want_other"),
        ],
        [
            InlineKeyboardButton(text="💰 Узнать цену", callback_data="want_price"),
        ],
    ])


def booking_keyboard() -> InlineKeyboardMarkup:
    """Кнопка записи на консультацию."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📐 Записаться на бесплатную консультацию", callback_data="book_measurement")],
        [InlineKeyboardButton(text="💬 Ещё вопросы", callback_data="more_questions")],
    ])


def confirm_booking_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение записи на замер."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_booking"),
        ],
    ])


def after_booking_keyboard() -> InlineKeyboardMarkup:
    """После записи на замер."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Посмотреть наши работы", callback_data="show_portfolio")],
        [InlineKeyboardButton(text="💬 Ещё вопросы", callback_data="more_questions")],
    ])
