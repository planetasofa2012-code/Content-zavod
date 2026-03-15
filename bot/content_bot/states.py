"""
FSM-состояния контент-бота.
"""

from aiogram.fsm.state import State, StatesGroup


class ContentStates(StatesGroup):
    """Состояния создания поста."""
    waiting_photo = State()          # Ожидание фото
    waiting_description = State()    # Ожидание описания (текст/голосовое)
    choosing_type = State()          # Выбор типа поста
    preview = State()                # Предпросмотр сгенерированного поста
    publishing = State()             # Процесс публикации
    interview_answer = State()       # Ожидание ответа на вопрос интервью
    waiting_idea = State()           # Ожидание идеи
    waiting_forward_photos = State() # Ожидание скриншотов переписки
    waiting_image_prompt = State()   # Ожидание описания картинки
