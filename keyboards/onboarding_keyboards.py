"""
Клавиатуры для процесса онбординга
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой "Пропустить" для опциональных полей.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭️ Пропустить")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой "Отмена".
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура с действиями для главного меню.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Рассчитать натальную карту",
                    callback_data="natal_chart"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Ежедневный прогноз",
                    callback_data="daily_forecast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💑 Совместимость",
                    callback_data="compatibility"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help"
                )
            ],
        ]
    )


def get_onboarding_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для ответа на приветствие.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )