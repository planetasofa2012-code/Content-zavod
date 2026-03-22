"""
Обработчики контент-бота.
Принимает фото + описание → генерирует посты → публикует.
"""

import logging
import base64
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.config import OWNER_ID
from bot.content_bot.states import ContentStates
from bot.content_bot.keyboards import (
    main_menu_keyboard, post_type_keyboard, preview_keyboard,
    interview_menu_keyboard, interview_after_answer_keyboard,
    image_result_keyboard,
)
from ai.openrouter import chat_with_vision, generate_text
from ai.prompts.post_generator import SYSTEM_PROMPT, get_post_generation_prompt
from ai.prompts.interviewer import get_random_question, get_answer_to_post_prompt
from ai.knowledge_base import save_to_knowledge_base
from db.supabase_client import save_post, save_knowledge

logger = logging.getLogger(__name__)


def safe_send(text: str, max_len: int = 4000) -> str:
    """Обрезает текст и убирает parse_mode если нужно."""
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text

router = Router()

# Фильтр: только Александр может пользоваться контент-ботом
router.message.filter(F.from_user.id == OWNER_ID)
router.callback_query.filter(F.from_user.id == OWNER_ID)


# === /start ===
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏭 **Контент-завод** — твой AI-помощник\n\n"
        "Отправь фото готовой мебели → я сделаю посты для всех площадок!",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )


# === Кнопка «Создать пост» ===
@router.callback_query(F.data == "create_post")
async def on_create_post(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ContentStates.waiting_photo)
    await callback.message.edit_text(
        "📸 Отправь фото готовой мебели!\n\n"
        "Можно одно фото или несколько.",
    )
    await callback.answer()


# === Получение фото ===
@router.message(ContentStates.waiting_photo, F.photo)
async def on_photo(message: Message, state: FSMContext, bot: Bot):
    # Сохраняем фото
    photo = message.photo[-1]  # Наилучшее качество
    file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file.file_path)
    photo_data = photo_bytes.getvalue() if hasattr(photo_bytes, 'getvalue') else photo_bytes.read()

    await state.update_data(photo_data=photo_data, photo_file_id=photo.file_id)
    await state.set_state(ContentStates.waiting_description)

    await message.answer(
        "✅ Фото получено!\n\n"
        "Теперь добавь описание:\n"
        "• Текстом: «Кухня МДФ эмаль, фурнитура Blum, скандинавский стиль»\n"
        "• Или голосовым сообщением 🎤",
    )


# === Получение описания (текст) ===
@router.message(ContentStates.waiting_description, F.text)
async def on_description_text(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ContentStates.choosing_type)
    await message.answer(
        "📋 Выбери тип поста (для воронки «3 касания»):",
        reply_markup=post_type_keyboard(),
    )


# === Выбор типа поста ===
@router.callback_query(ContentStates.choosing_type, F.data.startswith("type_"))
async def on_choose_type(callback: CallbackQuery, state: FSMContext):
    post_type = callback.data.replace("type_", "")
    await state.update_data(post_type=post_type)

    await callback.message.edit_text("⏳ Генерирую посты... Анализирую фото и пишу тексты")

    data = await state.get_data()

    # Проверяем наличие обязательных данных
    if "photo_data" not in data:
        await callback.message.edit_text(
            "❌ Фото не найдено. Начни заново /start"
        )
        await state.clear()
        return

    # 1. Анализ фото через Vision API
    vision_prompt = (
        "Опиши что на фото: тип мебели, стиль, материал фасадов, цвет, "
        "фурнитуру если видно, общее впечатление. Кратко, 2-3 предложения."
    )
    try:
        vision_analysis = await chat_with_vision(
            text=vision_prompt,
            image_bytes=data["photo_data"],
        )
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        vision_analysis = ""

    # 2. Генерация постов
    post_prompt = get_post_generation_prompt(
        description=data.get("description", "Мебель на заказ"),
        vision_analysis=vision_analysis,
        post_type=post_type,
    )

    try:
        generated = await generate_text(
            prompt=post_prompt,
            system_prompt=SYSTEM_PROMPT,
        )
    except Exception as e:
        logger.error(f"Generation error: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка генерации: {e}\n\nПопробуй ещё раз /start"
        )
        await state.clear()
        return

    await state.update_data(generated_posts=generated, vision_analysis=vision_analysis)
    await state.set_state(ContentStates.preview)

    # 3. Показать предпросмотр
    preview_text = (
        f"📋 Предпросмотр (тип: {post_type})\n\n"
        f"{generated}\n\n"
        f"─────────────\n"
        f"🔍 Vision: {vision_analysis[:200] if vision_analysis else 'не удалось'}..."
    )

    # Telegram ограничение: 4096 символов
    preview_text = safe_send(preview_text)

    await callback.message.edit_text(
        preview_text,
        reply_markup=preview_keyboard(),
    )
    await callback.answer()


# === Кнопка «Опубликовать» ===
@router.callback_query(ContentStates.preview, F.data == "publish")
async def on_publish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await callback.message.edit_text("📤 Публикую на площадки...")

    results = []

    # Публикация в Telegram
    try:
        from publishers.telegram_pub import publish_to_telegram
        await publish_to_telegram(
            bot=bot,
            photo_file_id=data["photo_file_id"],
            text=_extract_section(data["generated_posts"], "TELEGRAM"),
        )
        results.append("✅ Telegram")
    except Exception as e:
        logger.error(f"TG publish error: {e}")
        results.append(f"❌ Telegram: {e}")

    # Публикация в VK
    try:
        from publishers.vk_pub import publish_to_vk
        await publish_to_vk(
            photo_data=data["photo_data"],
            text=_extract_section(data["generated_posts"], "ВКОНТАКТЕ"),
        )
        results.append("✅ ВКонтакте")
    except Exception as e:
        logger.error(f"VK publish error: {e}")
        results.append(f"❌ ВКонтакте: {e}")

    # Сохраняем пост в Supabase
    try:
        tg_text = _extract_section(data["generated_posts"], "TELEGRAM")
        await save_post(
            title=tg_text[:80].split("\n")[0].strip(),
            content=tg_text,
            platforms=["telegram", "vk"],
            status="published",
            ai_generated=True,
        )
    except Exception as e:
        logger.error(f"Supabase save_post error: {e}")

    await callback.message.edit_text(
        "📊 **Результат публикации:**\n\n" +
        "\n".join(results) +
        "\n\n/start — создать ещё пост",
        parse_mode="Markdown",
    )
    await state.clear()
    await callback.answer()


# === Кнопка «Переделать» ===
@router.callback_query(ContentStates.preview, F.data == "regenerate")
async def on_regenerate(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ContentStates.choosing_type)
    await callback.message.edit_text(
        "✏️ Выбери тип поста заново:",
        reply_markup=post_type_keyboard(),
    )
    await callback.answer()


# === Кнопка «Отменить» ===
@router.callback_query(ContentStates.preview, F.data == "cancel")
async def on_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Отменено.\n\n/start — начать заново",
    )
    await callback.answer()


# === Идея — запись ===
@router.callback_query(F.data == "idea")
async def on_idea(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ContentStates.waiting_idea)
    await callback.message.edit_text(
        "💡 **Запись идеи**\n\n"
        "Напишите вашу идею по улучшению Контент-завода.\n"
        "Я сохраню её в папку `ideas/` как отдельный файл.\n\n"
        "Пишите 👇",
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(ContentStates.waiting_idea, F.text)
async def on_idea_text(message: Message, state: FSMContext):
    from datetime import datetime
    from pathlib import Path

    # Генерируем имя файла
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M") + ".md"
    ideas_dir = Path(__file__).parent.parent.parent / "ideas"
    ideas_dir.mkdir(exist_ok=True)
    filepath = ideas_dir / filename

    # Формируем контент
    content = f"# 💡 Идея — {now.strftime('%d.%m.%Y %H:%M')}\n\n"
    content += f"{message.text}\n"

    # Сохраняем (async-safe)
    import asyncio
    await asyncio.to_thread(filepath.write_text, content, "utf-8")

    # Считаем файлы
    idea_count = len(list(ideas_dir.glob("*.md"))) - 1  # минус README

    await state.clear()
    await message.answer(
        f"💡 **Идея сохранена!**\n\n"
        f"📁 Файл: `{filename}`\n"
        f"📊 Всего идей: {idea_count}\n\n"
        f"/start — в меню",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )


# === Статистика ===
@router.callback_query(F.data == "stats")
async def on_stats(callback: CallbackQuery, state: FSMContext):
    from ai.knowledge_base import load_knowledge_base
    from pathlib import Path

    kb = load_knowledge_base()
    ideas_dir = Path(__file__).parent.parent.parent / "ideas"

    # Считаем идеи
    idea_count = 0
    if ideas_dir.exists():
        idea_count = len([f for f in ideas_dir.glob("*.md") if f.name != "README.md"])

    # Категории знаний
    categories = {}
    for entry in kb:
        cat = entry.get("category", "другое")
        categories[cat] = categories.get(cat, 0) + 1

    cat_text = ""
    if categories:
        cat_lines = [f"  • {cat}: {count}" for cat, count in sorted(categories.items(), key=lambda x: -x[1])]
        cat_text = "\n".join(cat_lines)
    else:
        cat_text = "  Пока пусто"

    await callback.message.edit_text(
        f"📊 **Статистика Контент-завода**\n\n"
        f"🧠 **База знаний:** {len(kb)} записей\n"
        f"{cat_text}\n\n"
        f"💡 **Идеи:** {idea_count}\n\n"
        f"_Чем больше знаний — тем умнее AI-агент!_",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# === Меню интервью ===
@router.callback_query(F.data == "interview")
async def on_interview_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🎙️ **AI-Интервьюер**\n\n"
        "Я задам вопросы как клиент — ты ответишь.\n"
        "Ответы станут базой знаний AI-агента!",
        reply_markup=interview_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# === Полное интервью (гибрид: фиксированные + AI follow-up) ===
@router.callback_query(F.data == "interview_full")
async def on_interview_full(callback: CallbackQuery, state: FSMContext):
    from ai.prompts.interviewer import pick_question_for_interview

    interview_total = 6  # 3 фиксированных + 3 AI follow-up

    # Первый вопрос — всегда фиксированный
    pick = pick_question_for_interview(
        current_index=0,
        total=interview_total,
    )

    await state.update_data(
        interview_question=pick["question"],
        interview_category=pick["category"],
        interview_mode="full",
        interview_current=1,
        interview_total=interview_total,
        interview_asked=[pick["question"]],  # Трекинг заданных
    )
    await state.set_state(ContentStates.interview_answer)

    await callback.message.edit_text(
        f"🎙️ **Интервью** (вопрос 1/{interview_total})\n\n"
        f"💬 *«{pick['question']}»*\n\n"
        f"Ответь текстом 👇",
        parse_mode="Markdown",
    )
    await callback.answer()


# === Случайный вопрос ===
@router.callback_query(F.data == "interview_random")
async def on_interview_random(callback: CallbackQuery, state: FSMContext):
    question, category = get_random_question()
    await state.update_data(
        interview_question=question,
        interview_category=category,
        interview_mode="random",
    )
    await state.set_state(ContentStates.interview_answer)

    await callback.message.edit_text(
        f"🎙️ Вопрос от «клиента»:\n\n"
        f"💬 *«{question}»*\n\n"
        f"Ответь текстом или голосовым 👇",
        parse_mode="Markdown",
    )
    await callback.answer()


# === Голосовой ответ на интервью ===
@router.message(ContentStates.interview_answer, F.voice)
async def on_interview_voice(message: Message, state: FSMContext):
    """Обработка голосового ответа — транскрипция + сохранение."""
    await message.answer("🎤 Распознаю голосовое...")

    try:
        # Скачиваем голосовое
        file = await message.bot.get_file(message.voice.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        audio_data = file_bytes.read()

        # Транскрибируем
        from ai.transcribe import transcribe_voice
        text = await transcribe_voice(audio_data)

        if not text:
            await message.answer("❌ Не удалось распознать голосовое. Попробуйте текстом.")
            return

        await message.answer(f"📝 Распознано: *{text}*", parse_mode="Markdown")

        # Подставляем текст и вызываем текстовый обработчик
        message.text = text
        await on_interview_answer(message, state)

    except Exception as e:
        await message.answer(f"❌ Ошибка транскрипции: {e}\n\nПопробуйте текстом.")


# === Ответ на вопрос интервью → сохранение в базу знаний ===
@router.message(ContentStates.interview_answer, F.text)
async def on_interview_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data.get("interview_question", "")
    category = data.get("interview_category", "")
    mode = data.get("interview_mode", "random")

    # Сохраняем в локальную базу знаний (JSON)
    total = save_to_knowledge_base(
        question=question,
        answer=message.text,
        category=category,
    )

    # Дублируем в Supabase (для дашборда)
    try:
        await save_knowledge(
            question=question,
            answer=message.text,
            category=category,
            source="interview",
        )
    except Exception as e:
        logger.error(f"Supabase save_knowledge error: {e}")

    await state.update_data(last_answer=message.text)

    # Режим полного интервью — есть ещё вопросы?
    if mode == "full":
        current = data.get("interview_current", 1)
        interview_total = data.get("interview_total", 6)
        asked = data.get("interview_asked", [])

        if current < interview_total:
            # Выбираем следующий вопрос (гибрид)
            from ai.prompts.interviewer import pick_question_for_interview

            pick = pick_question_for_interview(
                current_index=current,
                total=interview_total,
                previous_question=question,
                previous_answer=message.text,
                asked_questions=asked,
            )

            next_question = ""
            next_category = pick.get("category", "")
            source_emoji = ""

            if pick["source"] == "fixed":
                # Фиксированный вопрос — сразу показываем
                next_question = pick["question"]
                source_emoji = "📋"
            else:
                # AI-вопрос — генерируем через OpenRouter
                source_emoji = "🤖"
                await message.answer(
                    f"💾 Сохранено! ({current}/{interview_total})\n\n"
                    f"🤖 AI думает над follow-up вопросом...",
                )
                try:
                    ai_question = await generate_text(prompt=pick["prompt"])
                    # Очищаем от кавычек и лишнего
                    next_question = ai_question.strip().strip("«»\"'💬 ")
                    if not next_question or len(next_question) < 5:
                        # Fallback на фиксированный
                        q, c = get_random_question()
                        next_question = q
                        next_category = c
                        source_emoji = "📋"
                except Exception as e:
                    logger.error(f"AI follow-up error: {e}")
                    q, c = get_random_question()
                    next_question = q
                    next_category = c
                    source_emoji = "📋"

            asked.append(next_question)
            await state.update_data(
                interview_question=next_question,
                interview_category=next_category,
                interview_current=current + 1,
                interview_asked=asked,
            )

            await message.answer(
                f"💾 Сохранено! ({current}/{interview_total})\n\n"
                f"🎙️ **Вопрос {current + 1}/{interview_total}** {source_emoji}\n\n"
                f"💬 *«{next_question}»*\n\n"
                f"Ответь текстом 👇",
                parse_mode="Markdown",
            )
            return
        else:
            # Интервью завершено!
            await message.answer(
                f"🎉 **Интервью завершено!**\n\n"
                f"💾 Сохранено ответов: {interview_total}\n"
                f"📊 Всего в базе знаний: {total}\n\n"
                f"AI-агент стал умнее! 🧠",
                reply_markup=interview_after_answer_keyboard(),
                parse_mode="Markdown",
            )
            return

    # Режим случайного вопроса
    await message.answer(
        f"💾 **Сохранено в базу знаний!**\n\n"
        f"📌 Категория: {category}\n"
        f"📊 Всего записей: {total}\n\n"
        f"AI-агент теперь знает ответ на этот вопрос! 🧠",
        reply_markup=interview_after_answer_keyboard(),
        parse_mode="Markdown",
    )


# === Переслать переписку (скриншоты) ===
@router.callback_query(F.data == "interview_forward")
async def on_interview_forward(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ContentStates.waiting_forward_photos)
    await state.update_data(forward_photos=[])
    await callback.message.edit_text(
        "📱 **Переслать переписку**\n\n"
        "Скиньте **скриншоты** переписки с клиентом.\n"
        "AI распознает вопросы и ответы → сохранит в базу знаний.\n\n"
        "Можно отправить несколько фото подряд.\n"
        "Когда закончите — напишите **Готово**",
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(ContentStates.waiting_forward_photos, F.photo)
async def on_forward_photo(message: Message, state: FSMContext):
    """Получаем скриншот переписки."""
    data = await state.get_data()
    photos = data.get("forward_photos", [])

    # Скачиваем фото
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file.file_path)
    raw = file_bytes.getvalue() if hasattr(file_bytes, 'getvalue') else file_bytes.read()
    photo_b64 = base64.b64encode(raw).decode()

    photos.append(photo_b64)
    await state.update_data(forward_photos=photos)

    await message.answer(
        f"📸 Скриншот {len(photos)} получен!\n"
        f"Скиньте ещё или напишите **Готово**",
        parse_mode="Markdown",
    )


@router.message(ContentStates.waiting_forward_photos, F.text)
async def on_forward_done(message: Message, state: FSMContext):
    """Обработка скриншотов через Vision API."""
    if message.text.lower().strip() not in ("готово", "done", "всё", "все"):
        await message.answer("Скиньте скриншоты или напишите **Готово**", parse_mode="Markdown")
        return

    data = await state.get_data()
    photos = data.get("forward_photos", [])

    if not photos:
        await message.answer("❌ Вы не отправили ни одного скриншота.\n\n/start")
        await state.clear()
        return

    await message.answer(f"⏳ Распознаю {len(photos)} скриншот(ов)...")

    # Обрабатываем каждый скриншот через Vision API
    # base64 импортирован в начале файла
    total_saved = 0
    for i, photo_b64 in enumerate(photos):
        try:
            photo_bytes = base64.b64decode(photo_b64)
            result = await chat_with_vision(
                image_bytes=photo_bytes,
                text=(
                    "На скриншоте переписка мебельщика с клиентом. "
                    "Извлеки ВСЕ пары вопрос-ответ.\n"
                    "Формат:\n"
                    "ВОПРОС: [вопрос клиента]\n"
                    "ОТВЕТ: [ответ мастера]\n"
                    "---\n"
                    "Если на скриншоте нет чёткой Q&A структуры, "
                    "выдели ключевые темы в том же формате."
                ),
            )

            # Парсим пары вопрос-ответ
            pairs = result.split("---")
            for pair in pairs:
                pair = pair.strip()
                q_pos = pair.find("ВОПРОС:")
                a_pos = pair.find("ОТВЕТ:")
                if q_pos != -1 and a_pos != -1 and a_pos > q_pos:
                    question = pair[q_pos + 7:a_pos].strip()
                    answer = pair[a_pos + 6:].strip()
                    if question and answer:
                        save_to_knowledge_base(
                            question=question,
                            answer=answer,
                            category="client_dialog",
                        )
                        total_saved += 1

        except Exception as e:
            await message.answer(f"⚠️ Ошибка скриншота {i+1}: {e}")

    from ai.knowledge_base import load_knowledge_base
    total_kb = len(load_knowledge_base())

    await state.clear()
    await message.answer(
        f"✅ **Готово!**\n\n"
        f"📸 Распознано скриншотов: {len(photos)}\n"
        f"💾 Сохранено Q&A пар: {total_saved}\n"
        f"📊 Всего в базе знаний: {total_kb}\n\n"
        f"AI-агент учится на реальных диалогах! 🧠",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )


# === Сделать пост из ответа интервью ===
@router.callback_query(F.data == "interview_to_post")
async def on_interview_to_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question = data.get("interview_question", "")
    answer = data.get("last_answer", "")

    await callback.message.edit_text("⏳ Генерирую пост из ответа...")

    post_prompt = get_answer_to_post_prompt(question, answer)
    try:
        generated = await generate_text(prompt=post_prompt)
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка генерации: {e}\n\n/start"
        )
        await state.clear()
        return

    await state.update_data(generated_posts=generated)
    await state.set_state(ContentStates.preview)

    preview_text = safe_send(f"📋 Пост из интервью:\n\n{generated}")

    await callback.message.edit_text(
        preview_text,
        reply_markup=preview_keyboard(),
    )
    await callback.answer()


# === Генерация картинок — шаг 1: спрашиваем ===
@router.callback_query(F.data == "gen_image")
async def on_gen_image(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ContentStates.waiting_image_prompt)
    await callback.message.edit_text(
        "🖼️ Какую картинку сделать?\n\n"
        "Опишите что нужно, например:\n"
        "• Белая кухня в современном интерьере\n"
        "• Шкаф-купе с зеркалом\n"
        "• Столешница из кварца крупным планом\n\n"
        "Или напишите «авто» — AI сам придумает по тексту поста 👇"
    )
    await callback.answer()


# === Генерация картинок — шаг 2: генерируем ===
@router.message(ContentStates.waiting_image_prompt, F.text)
async def on_gen_image_prompt(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        generated_posts = data.get("generated_posts", "")
        user_request = message.text.strip()

        # Если "авто" — используем AI для промпта
        if user_request.lower() in ("авто", "auto", "ai"):
            await message.answer("🤖 AI создаёт промпт из текста поста...")
            from ai.image_gen import generate_image_prompt
            img_prompt = await generate_image_prompt(generated_posts[:500])
        else:
            # Пользователь описал сам — переводим в промпт
            from ai.image_gen import generate_image_prompt
            img_prompt = await generate_image_prompt(user_request)

        await message.answer(
            f"⏳ Генерирую 3 варианта...\n"
            f"Промпт: {img_prompt[:150]}..."
        )

        from ai.image_gen import generate_images_openrouter
        from aiogram.types import BufferedInputFile, InputMediaPhoto

        images = await generate_images_openrouter(img_prompt, count=3)

        if images:
            media_group = []
            for i, img_bytes in enumerate(images):
                photo = BufferedInputFile(img_bytes, filename=f"variant_{i+1}.png")
                caption = f"🖼️ {len(images)} варианта | {user_request}" if i == 0 else None
                media_group.append(InputMediaPhoto(media=photo, caption=caption))

            await message.answer_media_group(media=media_group)

            await message.answer(
                "Не понравилось? Сгенерируем ещё!",
                reply_markup=image_result_keyboard(),
            )
        else:
            await message.answer(
                f"❌ Не удалось сгенерировать.\nПромпт: {img_prompt[:300]}\n\n"
                "Попробуйте описать картинку иначе.",
                reply_markup=image_result_keyboard(),
            )
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await message.answer(
            f"❌ Ошибка генерации: {e}\n\n/start",
        )

    await state.set_state(ContentStates.preview)


# === Назад к посту после картинок ===
@router.callback_query(F.data == "back_to_post")
async def on_back_to_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    generated_posts = data.get("generated_posts", "")
    await state.set_state(ContentStates.preview)
    await callback.message.edit_text(
        safe_send(f"📋 Пост:\n\n{generated_posts}"),
        reply_markup=preview_keyboard(),
    )
    await callback.answer()


# === Назад в главное меню ===
@router.callback_query(F.data == "back_main")
async def on_back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🏭 **Контент-завод** — твой AI-помощник\n\n"
        "Отправь фото готовой мебели → я сделаю посты для всех площадок!",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# === Утилиты ===
def _extract_section(text: str, section: str) -> str:
    """Извлекает секцию из сгенерированного текста (=== TELEGRAM === и т.д.)."""
    markers = {
        "TELEGRAM": ("=== TELEGRAM ===", "=== ВКОНТАКТЕ ==="),
        "ВКОНТАКТЕ": ("=== ВКОНТАКТЕ ===", "=== INSTAGRAM ==="),
        "INSTAGRAM": ("=== INSTAGRAM ===", "=== PINTEREST ==="),
        "PINTEREST": ("=== PINTEREST ===", None),
    }

    start_marker, end_marker = markers.get(section, (None, None))
    if not start_marker or start_marker not in text:
        return text[:500]  # Fallback: первые 500 символов

    start = text.index(start_marker) + len(start_marker)
    if end_marker and end_marker in text:
        end = text.index(end_marker)
    else:
        end = len(text)

    return text[start:end].strip()
