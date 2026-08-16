"""
Состояния для процесса онбординга (сбор данных пользователя)
"""
from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """
    Состояния для сбора данных пользователя.
    """
    WAITING_FOR_NAME = State()          # Ожидаем имя
    WAITING_FOR_LAST_NAME = State()     # Ожидаем фамилию (опционально)
    WAITING_FOR_BIRTH_DATE = State()    # Ожидаем дату рождения
    WAITING_FOR_BIRTH_TIME = State()    # Ожидаем время рождения
    WAITING_FOR_PLACE = State()         # Ожидаем место рождения
    DATA_COMPLETE = State()             # Данные собраны