"""
Обработчики AI-агента для клиентов.
Консультирует → собирает информацию → передаёт на расчёт КП.
Отправляет уведомления Александру о новых заявках.
"""

import logging
from datetime import datetime, timedelta
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
from bot.agent_bot.dialog_logger import start_session, log_message

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

    # Логирование: новая сессия
    start_session(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or "",
        source=source,
    )

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

    # Логирование сообщения клиента
    log_message(user_id, "user", user_text, "text")

    # Получить ответ AI
    response = await _get_ai_response(user_id, user_text)

    # Логирование ответа бота
    log_message(user_id, "assistant", response, "text")

    # Счётчик сообщений (для уведомлений)
    data = await state.get_data()
    msg_count = data.get("msg_count", 0) + 1
    await state.update_data(msg_count=msg_count)

    # Кнопку консультации показываем ТОЛЬКО после отправки КП
    # До расчёта — НИКОГДА не предлагаем замер/консультацию
    is_booked = data.get("booked", False)
    kp_sent = data.get("kp_sent", False)
    if _should_suggest_booking(response) and not is_booked and kp_sent:
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

    # Уведомление Александру когда клиент просит нерабочее время
    if _needs_schedule_check(response):
        try:
            await bot.send_message(
                OWNER_ID,
                f"⏰ **Запрос на нестандартное время!**\n\n"
                f"👤 Клиент: {message.from_user.full_name}\n"
                f"📱 TG: @{message.from_user.username or 'нет'}\n"
                f"🆔 ID: {message.from_user.id}\n\n"
                f"💬 Клиент написал: «{user_text[:300]}»\n\n"
                f"🤖 Бот ответил, что уточнит у вас.\n"
                f"Свяжитесь с клиентом, если можете подстроиться!",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления о расписании: {e}")

    # Уведомление Александру когда AI передаёт проект на расчёт КП
    if _needs_kp_request(response):
        try:
            # Собрать историю диалога
            chat_log = ""
            user_history = dialog_history.get(user_id, [])
            for msg in user_history[-20:]:
                role = "👤 Клиент" if msg["role"] == "user" else "🤖 Бот"
                text = msg["content"][:300]
                chat_log += f"{role}: {text}\n\n"

            await bot.send_message(
                OWNER_ID,
                f"📋 **ЗАПРОС НА РАСЧЁТ КП!**\n\n"
                f"👤 Клиент: {message.from_user.full_name}\n"
                f"📱 TG: @{message.from_user.username or 'нет'}\n"
                f"🆔 ID: {message.from_user.id}\n\n"
                f"Бот собрал информацию и передаёт вам на расчёт.\n"
                f"Сделайте КП и отправьте через бота!",
                parse_mode="Markdown",
            )
            # Историю диалога — отдельным сообщением
            if chat_log.strip():
                log_text = f"💬 **Диалог с {message.from_user.full_name}:**\n\n{chat_log}"
                if len(log_text) > 4000:
                    log_text = log_text[:3997] + "..."
                await bot.send_message(OWNER_ID, log_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка уведомления о КП: {e}")


# === Кнопка «Записаться на замер» ===
@router.callback_query(F.data == "book_measurement")
async def on_book_measurement(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AgentStates.booking_measurement)
    await callback.message.edit_text(
        "📐 Отлично! Для записи на бесплатную консультацию мне нужно:\n\n"
        "1. Ваше имя\n"
        "2. Удобная дата и время (пн-пт, с 9 до 17)\n"
        "3. Адрес\n\n"
        "Напишите всё в одном сообщении, например:\n"
        "«Иван, среда 10:00, ул. Ленина 5, кв. 12»",
    )
    await callback.answer()


# === Получение данных для замера ===
@router.message(AgentStates.booking_measurement, F.text)
async def on_booking_details(message: Message, state: FSMContext, bot: Bot):
    booking_text = message.text

    # Парсим через AI
    parse_prompt = f"""Клиент написал данные для записи на консультацию:
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

    # Уведомление Александру с полной историей диалога
    try:
        # Собрать историю из dialog_history
        chat_log = ""
        user_history = dialog_history.get(user.id, [])
        for msg in user_history[-16:]:
            role = "👤 Клиент" if msg["role"] == "user" else "🤖 Бот"
            text = msg["content"][:200]
            chat_log += f"{role}: {text}\n\n"

        notification = (
            f"🔔 **НОВАЯ КОНСУЛЬТАЦИЯ!**\n\n"
            f"👤 Клиент: {user.full_name}\n"
            f"📱 TG: @{user.username or 'нет'}\n"
            f"🆔 ID: {user.id}\n\n"
            f"📋 Данные записи:\n{data.get('booking_parsed', data.get('booking_raw', 'нет'))}\n\n"
            f"🪑 Тип мебели: {data.get('furniture_type', 'не указано')}\n"
            f"📊 Сообщений в диалоге: {data.get('msg_count', 0)}\n\n"
            f"⏰ Заявка от: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        await bot.send_message(OWNER_ID, notification, parse_mode="Markdown")

        # Отдельным сообщением — история диалога (может быть длинной)
        if chat_log.strip():
            # Обрезаем до 4000 символов (лимит Telegram)
            log_text = f"💬 **История диалога с {user.full_name}:**\n\n{chat_log}"
            if len(log_text) > 4000:
                log_text = log_text[:3997] + "..."
            await bot.send_message(OWNER_ID, log_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка уведомления о консультации: {e}")

    # Помечаем что клиент уже записан — не предлагать повторно
    await state.update_data(booked=True)
    await state.set_state(AgentStates.chatting)

    await callback.message.edit_text(
        "✅ Записано! Александр свяжется с вами для подтверждения.\n\n"
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
        "📸 О, спасибо за фото! Вы хотите что-то подобное?\n\n"
        "Расскажите подробнее — что именно нравится на картинке? "
        "Цвет, форма, стиль? Я передам мастеру 😊",
    )


# === Обработка голосовых сообщений ===
@router.message(AgentStates.chatting, F.voice)
async def on_client_voice(message: Message, state: FSMContext, bot: Bot):
    """Распознаёт голосовое через Whisper и обрабатывает как текст."""
    try:
        # Скачиваем аудио
        file = await bot.get_file(message.voice.file_id)
        audio_data = await bot.download_file(file.file_path)
        audio_bytes = audio_data.read()

        # Транскрибируем через Whisper
        from ai.transcribe import transcribe_voice
        text = await transcribe_voice(audio_bytes)

        if not text or not text.strip():
            await message.answer(
                "🎤 Не удалось разобрать голосовое — попробуйте ещё раз "
                "или напишите текстом 😊"
            )
            return

        logger.info(f"🎤 Голосовое от {message.from_user.full_name}: {text[:100]}...")

        # Показываем клиенту что мы поняли
        await message.answer(f"🎤 Услышал(а): «{text[:200]}»\n\nСейчас отвечу...")

        # Обрабатываем как обычное текстовое сообщение
        user_id = message.from_user.id

        # Логирование голосового
        log_message(user_id, "user", text, "voice")

        response = await _get_ai_response(user_id, text)

        # Логирование ответа бота
        log_message(user_id, "assistant", response, "text")

        data = await state.get_data()
        msg_count = data.get("msg_count", 0) + 1
        await state.update_data(msg_count=msg_count)

        is_booked = data.get("booked", False)
        if _should_suggest_booking(response) and not is_booked:
            await message.answer(response, reply_markup=booking_keyboard())
        else:
            await message.answer(response)

        # Уведомление о первом сообщении
        if msg_count == 1:
            try:
                source = data.get("source", "")
                source_text = "📢 из канала @kuhnya154" if source == "from_channel" else "🔍 напрямую"
                await bot.send_message(
                    OWNER_ID,
                    f"👤 **Новый клиент!**\n\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Источник: {source_text}\n"
                    f"Первое сообщение (голосовое): «{text[:200]}»\n"
                    f"Диалог ведёт AI-агент",
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить владельца: {e}")

        # Проверки на КП и расписание
        if _needs_schedule_check(response):
            try:
                await bot.send_message(
                    OWNER_ID,
                    f"⏰ **Запрос на нестандартное время!**\n\n"
                    f"👤 Клиент: {message.from_user.full_name}\n"
                    f"💬 Клиент сказал (голосовое): «{text[:300]}»\n\n"
                    f"🤖 Бот ответил, что уточнит у вас.",
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления: {e}")

        if _needs_kp_request(response):
            try:
                chat_log = ""
                user_history = dialog_history.get(user_id, [])
                for msg in user_history[-20:]:
                    role = "👤 Клиент" if msg["role"] == "user" else "🤖 Бот"
                    chat_log += f"{role}: {msg['content'][:300]}\n\n"
                await bot.send_message(
                    OWNER_ID,
                    f"📋 **ЗАПРОС НА РАСЧЁТ КП!**\n\n"
                    f"👤 Клиент: {message.from_user.full_name}\n"
                    f"📱 TG: @{message.from_user.username or 'нет'}\n\n"
                    f"Бот собрал информацию и передаёт вам на расчёт.",
                    parse_mode="Markdown",
                )
                if chat_log.strip():
                    log_text = f"💬 **Диалог с {message.from_user.full_name}:**\n\n{chat_log}"
                    if len(log_text) > 4000:
                        log_text = log_text[:3997] + "..."
                    await bot.send_message(OWNER_ID, log_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Ошибка уведомления о КП: {e}")

    except RuntimeError:
        await message.answer(
            "🎤 Не удалось распознать голосовое — попробуйте ещё раз "
            "или напишите текстом 😊"
        )
    except Exception as e:
        logger.error(f"Ошибка обработки голосового: {e}")
        await message.answer(
            "😔 Произошла ошибка при обработке голосового сообщения. "
            "Попробуйте написать текстом!"
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

    # Собрать сообщения для AI с актуальной датой/временем
    now = datetime.now()
    day_names = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    current_day = day_names[now.weekday()]
    is_weekend = now.weekday() >= 5  # суббота=5, воскресенье=6
    is_late = now.hour >= 18

    time_context = (
        f"\n\n═══════════════════════════════════════\n"
        f"ТЕКУЩЕЕ ВРЕМЯ (учитывай при планировании замеров!):\n"
        f"═══════════════════════════════════════\n"
        f"Сейчас: {now.strftime('%d.%m.%Y')} ({current_day}), {now.strftime('%H:%M')}\n"
    )
    if is_weekend:
        time_context += "⚠️ СЕГОДНЯ ВЫХОДНОЙ! Консультации можно планировать только на будний день (пн-пт).\n"
    if is_late:
        time_context += "⚠️ СЕЙЧАС ПОЗДНИЙ ВЕЧЕР! На сегодня консультация невозможна. Предлагай на следующий рабочий день утром.\n"

    # Рассчитать ближайший рабочий день
    next_work = now
    while True:
        next_work = next_work + timedelta(days=1)
        if next_work.weekday() < 5:  # пн-пт
            next_day_name = day_names[next_work.weekday()]
            time_context += f"📅 Ближайший рабочий день: {next_day_name}, {next_work.strftime('%d.%m.%Y')}\n"
            break

    prompt_with_time = AGENT_SYSTEM_PROMPT + time_context

    messages = [{"role": "system", "content": prompt_with_time}]
    messages.extend(dialog_history[user_id])

    try:
        response = await chat(messages, temperature=0.7, max_tokens=1000)
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
    """Проверяет, предлагает ли AI замер в ответе."""
    keywords = ["замер", "приехать", "приедет", "записать", "выезд", "приедем", "консультац"]
    response_lower = response.lower()
    return any(kw in response_lower for kw in keywords)


def _needs_schedule_check(response: str) -> bool:
    """Проверяет, обещает ли AI уточнить у мастера по поводу времени."""
    response_lower = response.lower()
    check_keywords = ["передам александру", "уточню у александра", "свяжется с вами", "свяжется александр"]
    time_keywords = ["вечер", "выходн", "суббот", "воскресен"]
    # Срабатывает только если есть и фраза про передачу, и контекст времени
    has_transfer = any(kw in response_lower for kw in check_keywords)
    has_time = any(kw in response_lower for kw in time_keywords)
    return has_transfer and has_time


def _needs_kp_request(response: str) -> bool:
    """Проверяет, передаёт ли AI информацию мастеру на расчёт КП."""
    response_lower = response.lower()
    # AI говорит что передаёт мастеру / Александру на расчёт
    kp_keywords = [
        "передаю мастеру", "передам мастеру",
        "передаю александру", "передам александру",
        "рассчитает", "сделает расчёт",
        "пришлю предложение", "пришлю вам предложение",
    ]
    return any(kw in response_lower for kw in kp_keywords)
