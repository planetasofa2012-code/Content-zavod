"""
FSM-состояния AI-агента для клиентов.
"""

from aiogram.fsm.state import State, StatesGroup


class AgentStates(StatesGroup):
    """Состояния диалога с клиентом."""
    chatting = State()              # Свободный диалог (основное состояние)
    collecting_brief = State()      # Сбор брифа (размеры, материал, бюджет)
    booking_measurement = State()   # Запись на замер (дата, время, адрес)
    confirming_booking = State()    # Подтверждение записи
