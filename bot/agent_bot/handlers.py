"""
Обработчики AI-агента для клиентов.
Консультирует → рассчитывает → записывает на замер.
Отправляет уведомления Александру о новых заявках.
"""

import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from bot.config import OWNER_ID
from bot.agent_bot.states import AgentStates
from bot.agent_bot.keyboards import (
    welcome_keyboard,
    booking_keyboard,
    confirm_booking_keyboard,
    after_booking_keyboard,
)
from ai.openrouter import generate_text, chat
from ai.prompts.agent_system import AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

router = Router()

# Хранилище истории диалогов (в памяти, потом → Supabase)
dialog_history: dict[int, list[dict]] = {}

# Максимум сообщений в контексте AI
MAX_HISTORY = 20


# === /start ===
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    user = message.from_user
    source = command.args or ""  # deep-link параметр (?start=from_channel)
    logger.info(f"Новый клиент: {user.full_name} (id={user.id}, source={source})")

    # Сбросить состояние и историю
    await state.clear()
    dialog_history[user.id] = []

    await state.set_state(AgentStates.chatting)
    await state.update_data(source=source)

    # Персонализированное приветствие для клиентов из канала
    if source == "from_channel":
        await message.answer(
            f"Здравствуйте, {user.first_name}! 😊\n\n"
            "Рады, что вам понравились наши работы в канале! 🔥\n"
            "Расскажите, что вам приглянулось — или нажмите кнопку:",
            reply_markup=welcome_keyboard(),
        )
    else:
        await message.answer(
            f"Здравствуйте, {user.first_name}! 😊\n\n"
            "Я помогу с выбором мебели на заказ.\n"
            "Расскажите, что вы ищете — или нажмите кнопку:",
            reply_markup=welcome_keyboard(),
        )


# === Кнопки выбора типа мебели ===
@router.callback_query(F.data.startswith("want_"))
async def on_want_type(callback: CallbackQuery, state: FSMContext):
    furniture_map = {
        "want_kitchen": ("кухню", "кухни"),
        "want_wardrobe": ("шкаф", "шкафа"),
        "want_closet": ("гардеробную", "гардеробной"),
        "want_other": ("мебель", "мебели"),
        "want_price": ("мебель", "мебели"),
    }

    item, item_gen = furniture_map.get(callback.data, ("мебель", "мебели"))
    await state.update_data(furniture_type=item)
    await state.set_state(AgentStates.chatting)

    # Генерируем приветственный ответ через AI
    user_msg = f"Я хочу заказать {item}"
    response = await _get_ai_response(callback.from_user.id, user_msg)

    await callback.message.edit_text(response)
    await callback.answer()


# === Свободный диалог (основной обработчик) ===
@router.message(AgentStates.chatting, F.text)
async def on_client_message(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user_text = message.text

    # Получить ответ AI
    response = await _get_ai_response(user_id, user_text)

    # Проверяем, не пора ли предложить замер
    data = await state.get_data()
    msg_count = data.get("msg_count", 0) + 1
    await state.update_data(msg_count=msg_count)

    # После 3+ сообщений или если AI упоминает замер — показываем кнопку
    if msg_count >= 3 or _should_suggest_booking(response):
        await message.answer(response, reply_markup=booking_keyboard())
    else:
        await message.answer(response)

    # Уведомление Александру о новом клиенте (первое сообщение)
    if msg_count == 1:
        try:
            source = data.get("source", "")
            source_text = "📢 из канала @kuhnya154" if source == "from_channel" else "🔍 напрямую"
            await bot.send_message(
                OWNER_ID,
                f"👤 **Новый клиент!**\n\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Источник: {source_text}\n"
                f"Первое сообщение: «{user_text[:200]}»\n"
                f"Диалог ведёт AI-агент",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить владельца: {e}")


# === Кнопка «Записаться на замер» ===
@router.callback_query(F.data == "book_measurement")
async def on_book_measurement(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgentStates.booking_measurement)
    await callback.message.edit_text(
        "📐 Отлично! Для записи на бесплатный замер мне нужно:\n\n"
        "1. Ваше имя\n"
        "2. Удобная дата и время\n"
        "3. Адрес\n\n"
        "Напишите всё в одном сообщении, например:\n"
        "«Иван, среда после 15:00, ул. Ленина 5, кв. 12»",
    )
    await callback.answer()


# === Получение данных для замера ===
@router.message(AgentStates.booking_measurement, F.text)
async def on_booking_details(message: Message, state: FSMContext, bot: Bot):
    booking_text = message.text

    # Парсим через AI
    parse_prompt = f"""Клиент написал данные для записи на замер:
«{booking_text}»

Извлеки информацию в формате:
Имя: [имя]
Дата/время: [дата и время]
Адрес: [адрес]
Дополнительно: [если есть]

Если чего-то не хватает, напиши «не указано»."""

    parsed = await generate_text(parse_prompt, temperature=0.1)

    await state.update_data(booking_raw=booking_text, booking_parsed=parsed)
    await state.set_state(AgentStates.confirming_booking)

    await message.answer(
        f"📋 Проверьте данные:\n\n{parsed}\n\n"
        "Всё верно?",
        reply_markup=confirm_booking_keyboard(),
    )


# === Подтверждение записи ===
@router.callback_query(AgentStates.confirming_booking, F.data == "confirm_booking")
async def on_confirm_booking(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = callback.from_user

    # Уведомление Александру
    try:
        notification = (
            f"🔔 **НОВЫЙ ЗАМЕР!**\n\n"
            f"👤 Клиент: {user.full_name}\n"
            f"📱 TG: @{user.username or 'нет'}\n"
            f"🆔 ID: {user.id}\n\n"
            f"📋 Данные:\n{data.get('booking_parsed', data.get('booking_raw', 'нет'))}\n\n"
            f"🪑 Тип мебели: {data.get('furniture_type', 'не указано')}\n"
            f"📊 Сообщений в диалоге: {data.get('msg_count', 0)}\n\n"
            f"⏰ Заявка от: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        await bot.send_message(OWNER_ID, notification, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка уведомления о замере: {e}")

    await state.set_state(AgentStates.chatting)

    await callback.message.edit_text(
        "✅ Записано! Мастер Александр свяжется с вами для подтверждения.\n\n"
        "Спасибо, что выбрали нас! 😊\n\n"
        "А пока — может, хотите посмотреть наши работы?",
        reply_markup=after_booking_keyboard(),
    )
    await callback.answer()


# === Изменить данные замера ===
@router.callback_query(AgentStates.confirming_booking, F.data == "edit_booking")
async def on_edit_booking(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgentStates.booking_measurement)
    await callback.message.edit_text(
        "✏️ Напишите данные заново:\n"
        "Имя, дата/время, адрес",
    )
    await callback.answer()


# === Кнопка «Ещё вопросы» ===
@router.callback_query(F.data == "more_questions")
async def on_more_questions(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgentStates.chatting)
    await callback.message.edit_text(
        "💬 Конечно! Спрашивайте что угодно — "
        "я расскажу про материалы, цены, сроки, фурнитуру 😊",
    )
    await callback.answer()


# === Портфолио ===
@router.callback_query(F.data == "show_portfolio")
async def on_show_portfolio(callback: CallbackQuery, state: FSMContext):
    # TODO: подтягивать реальные фото из Supabase
    await callback.message.edit_text(
        "📸 Наши работы можете посмотреть:\n\n"
        "📱 Telegram: @kuhnya154\n"
        "💻 VK: vk.com/kuhnya54\n\n"
        "Там фото, кейсы и отзывы клиентов!\n\n"
        "💬 Есть ещё вопросы? Пишите!",
    )
    await callback.answer()


# === Обработка фото от клиента ===
@router.message(AgentStates.chatting, F.photo)
async def on_client_photo(message: Message, state: FSMContext):
    await message.answer(
        "📸 Красивое фото! Вы хотите что-то подобное?\n\n"
        "Расскажите подробнее — какой размер, материал, бюджет? "
        "Я помогу подобрать вариант 😊",
    )


# ========================
# Приватные функции
# ========================

async def _get_ai_response(user_id: int, user_message: str) -> str:
    """Получить ответ AI-агента с учётом истории диалога."""
    # Инициализация истории
    if user_id not in dialog_history:
        dialog_history[user_id] = []

    # Добавить сообщение клиента
    dialog_history[user_id].append({"role": "user", "content": user_message})

    # Обрезать историю (MAX_HISTORY последних сообщений)
    if len(dialog_history[user_id]) > MAX_HISTORY:
        dialog_history[user_id] = dialog_history[user_id][-MAX_HISTORY:]

    # Собрать сообщения для AI
    messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
    messages.extend(dialog_history[user_id])

    try:
        response = await chat(messages, temperature=0.7, max_tokens=500)
    except Exception as e:
        logger.error(f"AI error for user {user_id}: {e}")
        response = (
            "Прошу прощения, произошла техническая ошибка 😔\n"
            "Попробуйте написать ещё раз или "
            "свяжитесь с мастером напрямую: @kuhnya54"
        )

    # Сохранить ответ в историю
    dialog_history[user_id].append({"role": "assistant", "content": response})

    return response


def _should_suggest_booking(response: str) -> bool:
    """Проверяет, упоминает ли AI замер в ответе."""
    keywords = ["замер", "приехать", "приедет", "записать", "бесплатн"]
    response_lower = response.lower()
    return any(kw in response_lower for kw in keywords)
