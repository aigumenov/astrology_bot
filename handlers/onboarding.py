"""
Модуль 1: Greeting & Onboarding + User Data Collection

Отвечает за:
1. Приветствие пользователя
2. Сбор имени, фамилии (опционально), даты и времени рождения
3. Валидацию введенных данных
4. Сохранение в JSON-файл в папке пользователя
"""
import logging
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states.onboarding_states import OnboardingStates
from keyboards.onboarding_keyboards import (
    get_skip_keyboard,
    get_cancel_keyboard,
    get_actions_keyboard,
    get_onboarding_keyboard
)
from infrastructure.validators import (
    validate_name,
    validate_birth_date,
    validate_birth_time,
    validate_place
)
from storage.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

# Инициализируем репозиторий
user_repo = UserRepository()


# ---------- Хендлеры онбординга ----------

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    Начинает процесс онбординга.
    """
    # Проверяем, есть ли уже данные пользователя
    user_data = user_repo.load_user_data(str(message.from_user.id))
    
    if user_data:
        # Если пользователь уже зарегистрирован
        await message.answer(
            f"👋 С возвращением, {user_data.get('first_name', 'Друг')}!\n\n"
            "Твои данные уже сохранены. Что хочешь сделать?",
            reply_markup=get_actions_keyboard()
        )
        await state.clear()
        return
    
    # Начинаем процесс регистрации
    await message.answer(
        "🌟 Привет! Я твой астрологический помощник.\n\n"
        "Давай я создам твою натальную карту, чтобы я мог давать тебе персонализированные прогнозы и рекомендации.\n\n"
        "Для этого мне понадобится несколько данных о тебе. Это займет всего пару минут!\n\n"
        "📝 Пожалуйста, напиши свое имя:",
        reply_markup=get_cancel_keyboard()
    )
    
    # Устанавливаем состояние ожидания имени
    await state.set_state(OnboardingStates.WAITING_FOR_NAME)
    await state.update_data({})


@router.message(OnboardingStates.WAITING_FOR_NAME)
async def process_name(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода имени.
    """
    # Проверяем отмену
    if message.text == "❌ Отмена":
        await message.answer(
            "👋 Отменяю. Если захочешь начать снова, напиши /start",
            reply_markup=None
        )
        await state.clear()
        return
    
    # Валидируем имя
    is_valid, error = validate_name(message.text)
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\n"
            "Пожалуйста, напиши свое имя заново:"
        )
        return
    
    # Сохраняем имя
    await state.update_data(first_name=message.text.strip())
    
    # Спрашиваем фамилию (опционально)
    await message.answer(
        f"Отлично, {message.text.strip()}! 😊\n\n"
        "Теперь напиши свою фамилию.\n"
        "Это необязательно, можешь пропустить, нажав кнопку ниже:",
        reply_markup=get_skip_keyboard()
    )
    
    await state.set_state(OnboardingStates.WAITING_FOR_LAST_NAME)


@router.message(OnboardingStates.WAITING_FOR_LAST_NAME)
async def process_last_name(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода фамилии.
    """
    # Проверяем отмену
    if message.text == "❌ Отмена":
        await message.answer(
            "👋 Отменяю. Если захочешь начать снова, напиши /start",
            reply_markup=None
        )
        await state.clear()
        return
    
    # Проверяем пропуск
    if message.text == "⏭️ Пропустить":
        await state.update_data(last_name=None)
    else:
        # Сохраняем фамилию
        await state.update_data(last_name=message.text.strip())
    
    # Переходим к дате рождения
    await message.answer(
        "📅 Теперь напиши свою дату рождения в формате **ДД-ММ-ГГГГ**\n\n"
        "Например: 25-11-1986\n\n"
        "Или нажми /cancel для отмены",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OnboardingStates.WAITING_FOR_BIRTH_DATE)


@router.message(OnboardingStates.WAITING_FOR_BIRTH_DATE)
async def process_birth_date(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода даты рождения.
    """
    # Проверяем отмену
    if message.text == "❌ Отмена":
        await message.answer(
            "👋 Отменяю. Если захочешь начать снова, напиши /start",
            reply_markup=None
        )
        await state.clear()
        return
    
    # Валидируем дату
    is_valid, error, birth_date = validate_birth_date(message.text)
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\n"
            "Пожалуйста, напиши дату в формате **ДД-ММ-ГГГГ**:"
        )
        return
    
    # Сохраняем дату
    await state.update_data(birth_date=message.text.strip())
    await state.update_data(birth_date_obj=birth_date)
    
    # Переходим ко времени рождения
    await message.answer(
        "⏰ Теперь напиши время рождения в формате **ЧЧ-ММ**\n\n"
        "Например: 06-10\n\n"
        "💡 Если не знаешь точное время, можно указать примерно (например, 12-00), но это влияет на точность карты.",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(OnboardingStates.WAITING_FOR_BIRTH_TIME)


@router.message(OnboardingStates.WAITING_FOR_BIRTH_TIME)
async def process_birth_time(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода времени рождения.
    """
    # Проверяем отмену
    if message.text == "❌ Отмена":
        await message.answer(
            "👋 Отменяю. Если захочешь начать снова, напиши /start",
            reply_markup=None
        )
        await state.clear()
        return
    
    # Валидируем время
    is_valid, error, time_tuple = validate_birth_time(message.text)
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\n"
            "Пожалуйста, напиши время в формате **ЧЧ-ММ**:"
        )
        return
    
    hour, minute = time_tuple
    await state.update_data(birth_time=message.text.strip())
    await state.update_data(birth_hour=hour)
    await state.update_data(birth_minute=minute)
    
    # Собираем все данные и сохраняем
    user_data = await state.get_data()
    
    # Генерируем username
    username = user_repo.generate_username(
        user_data.get('first_name'),
        user_data.get('last_name')
    )
    
    # Формируем структуру данных
    user_profile = {
        "user_id": str(message.from_user.id),
        "first_name": user_data.get('first_name'),
        "last_name": user_data.get('last_name'),
        "birth_date": user_data.get('birth_date'),
        "birth_time": user_data.get('birth_time'),
        "birth_place": None,  # Будет добавлено позже
        "latitude": None,
        "longitude": None,
        "timezone": "Europe/Moscow",
        "registered_at": datetime.now().isoformat(),
        "username": username,
        "status": "active",
        "tariff": "free"
    }
    
    # Сохраняем данные
    user_repo.save_user_data(username, user_profile)
    
    # Показываем результат
    response = (
        f"✅ Отлично, {user_data.get('first_name')}! 🎉\n\n"
        f"Я сохранил твои данные:\n"
        f"📝 Имя: {user_data.get('first_name')}\n"
        f"📝 Фамилия: {user_data.get('last_name') or 'Не указана'}\n"
        f"📅 Дата рождения: {user_data.get('birth_date')}\n"
        f"⏰ Время рождения: {user_data.get('birth_time')}\n\n"
        f"📁 Данные сохранены в папку: data/user_data/{username}/\n\n"
        f"Теперь я готов рассчитать твою натальную карту! 🧙‍♂️\n\n"
        f"Что ты хочешь сделать дальше?"
    )
    
    await message.answer(
        response,
        reply_markup=get_actions_keyboard()
    )
    
    # Завершаем FSM
    await state.clear()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /cancel.
    Отменяет текущий диалог.
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного диалога для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "👋 Диалог отменен. Если захочешь начать снова, напиши /start",
        reply_markup=None
    )


@router.callback_query(F.data == "natal_chart")
async def callback_natal_chart(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик нажатия на кнопку "Рассчитать натальную карту".
    """
    await callback.answer()
    
    user_data = user_repo.load_user_data(str(callback.from_user.id))
    
    if not user_data:
        await callback.message.edit_text(
            "⚠️ Твои данные не найдены. Пожалуйста, начни с /start"
        )
        return
    
    await callback.message.edit_text(
        "🔮 Хорошо! Сейчас я рассчитаю твою натальную карту..."
    )
    
    # Здесь будет вызов модуля расчета натальной карты
    # (будет добавлен позже)


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery) -> None:
    """
    Обработчик нажатия на кнопку "Помощь".
    """
    await callback.answer()
    
    help_text = (
        "ℹ️ **Помощь по боту**\n\n"
        "🤖 Я — астрологический бот. Мои возможности:\n\n"
        "📊 **Натальная карта** — построю твою карту рождения\n"
        "📅 **Ежедневный прогноз** — подскажу, что ждать сегодня\n"
        "💑 **Совместимость** — сравню карты с партнером\n\n"
        "📝 **Команды:**\n"
        "/start — начать работу\n"
        "/cancel — отменить действие\n"
        "/help — помощь\n\n"
        "💡 Все данные сохраняются в папке user_data/твой_username/"
    )
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_actions_keyboard()
    )


@router.callback_query(F.data == "daily_forecast")
async def callback_daily_forecast(callback: CallbackQuery) -> None:
    """
    Обработчик нажатия на кнопку "Ежедневный прогноз".
    """
    await callback.answer("🔮 Ежедневный прогноз будет доступен после расчета натальной карты!")
    await callback.message.answer(
        "🔮 Для получения ежедневного прогноза сначала рассчитай натальную карту.\n\n"
        "Нажми 'Рассчитать натальную карту' в главном меню."
    )


@router.callback_query(F.data == "compatibility")
async def callback_compatibility(callback: CallbackQuery) -> None:
    """
    Обработчик нажатия на кнопку "Совместимость".
    """
    await callback.answer("💑 Функция совместимости будет доступна позже!")
    await callback.message.answer(
        "💑 Функция совместимости в разработке. Скоро она появится!"
    )


# ---------- Регистрация роутера ----------
def register_onboarding_handlers(dp):
    """
    Регистрирует хендлеры онбординга в диспетчере.
    """
    dp.include_router(router)