#!/usr/bin/env python3
"""
Полный бот для мессенджера MAX с графическим интерфейсом

Функции:
- Приветствие и сбор данных пользователя
- Сохранение данных в JSON
- Натальная карта
- Транзиты (ежедневный прогноз)
- Солярное возвращение
- Синастрия (совместимость)
- Полный отчет

Запуск:
    python max_bot.py

Требования:
    pip install fastapi uvicorn httpx
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import httpx

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from storage import UserRepository
from core import (
    SubjectFactory,
    NatalCalculator,
    AspectsCalculator,
    ChartDrawer,
    TransitsCalculator,
    ReturnsCalculator,
    EphemerisGenerator,
    SynastryCalculator
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== Конфигурация ====================

class Config:
    """Конфигурация бота."""
    # MAX Bot API (замените на ваш токен)
    MAX_BOT_TOKEN = "YOUR_MAX_BOT_TOKEN"
    MAX_API_URL = "https://api.max.ru/bot/v1"
    
    # Настройки сервера
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Пути
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    USER_DATA_DIR = DATA_DIR / "user_data"
    
    # Создаем папки
    DATA_DIR.mkdir(exist_ok=True)
    USER_DATA_DIR.mkdir(exist_ok=True)


# ==================== Инициализация ====================

user_repo = UserRepository(str(Config.USER_DATA_DIR))

# ==================== Pydantic модели ====================

class UserData(BaseModel):
    """Данные пользователя."""
    first_name: str
    last_name: Optional[str] = None
    birth_date: str
    birth_time: str
    place: str
    latitude: float = 47.2357
    longitude: float = 39.7015
    timezone: str = "Europe/Moscow"
    chat_id: Optional[str] = None
    username: Optional[str] = None

class MaxWebhookRequest(BaseModel):
    """Входящий запрос от MAX."""
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    user_id: Optional[str] = None
    text: Optional[str] = None
    callback_data: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

class MaxSendMessage(BaseModel):
    """Исходящее сообщение в MAX."""
    chat_id: str
    text: str
    reply_markup: Optional[Dict[str, Any]] = None


# ==================== FastAPI приложение ====================

app = FastAPI(
    title="MAX Astrology Bot",
    description="Астрологический бот для мессенджера MAX",
    version="1.0.0"
)


# ==================== MAX API клиент ====================

class MaxBotAPI:
    """Клиент для работы с MAX Bot API."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = Config.MAX_API_URL
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, chat_id: str, text: str, reply_markup: Optional[Dict] = None):
        """Отправляет сообщение."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()
    
    async def send_photo(self, chat_id: str, photo: str, caption: Optional[str] = None):
        """Отправляет фото."""
        url = f"{self.base_url}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo
        }
        if caption:
            payload["caption"] = caption
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()
    
    async def edit_message_text(self, chat_id: str, message_id: str, text: str, reply_markup: Optional[Dict] = None):
        """Редактирует сообщение."""
        url = f"{self.base_url}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()
    
    async def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None):
        """Отвечает на callback запрос."""
        url = f"{self.base_url}/answerCallbackQuery"
        payload = {
            "callback_query_id": callback_query_id
        }
        if text:
            payload["text"] = text
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()


# ==================== Клавиатуры ====================

def get_main_menu_keyboard():
    """Главное меню."""
    return {
        "inline_keyboard": [
            [
                {"text": "📊 Натальная карта", "callback_data": "natal"},
                {"text": "🔮 Ежедневный прогноз", "callback_data": "daily"}
            ],
            [
                {"text": "🌞 Солярное возвращение", "callback_data": "solar"},
                {"text": "💑 Совместимость", "callback_data": "synastry"}
            ],
            [
                {"text": "📄 Полный отчет", "callback_data": "report"},
                {"text": "🔄 Обновить данные", "callback_data": "update_data"}
            ],
            [
                {"text": "❓ Помощь", "callback_data": "help"}
            ]
        ]
    }


def get_cancel_keyboard():
    """Клавиатура отмены."""
    return {
        "inline_keyboard": [
            [{"text": "❌ Отмена", "callback_data": "cancel"}]
        ]
    }


def get_skip_keyboard():
    """Клавиатура с пропуском."""
    return {
        "inline_keyboard": [
            [{"text": "⏭️ Пропустить", "callback_data": "skip"}],
            [{"text": "❌ Отмена", "callback_data": "cancel"}]
        ]
    }


def get_back_keyboard():
    """Клавиатура возврата."""
    return {
        "inline_keyboard": [
            [{"text": "🔙 Назад", "callback_data": "back"}]
        ]
    }


# ==================== Логика бота ====================

class AstrologyBot:
    """Основная логика бота."""
    
    def __init__(self):
        self.max_api = MaxBotAPI(Config.MAX_BOT_TOKEN)
        self.user_repo = user_repo
        self.user_sessions = {}  # Временное хранилище для сессий
    
    async def handle_webhook(self, request: Request):
        """Обрабатывает входящий вебхук от MAX."""
        try:
            data = await request.json()
            logger.info(f"Получен webhook: {data}")
            
            # Определяем тип запроса
            if "callback_query" in data:
                return await self._handle_callback(data)
            else:
                return await self._handle_message(data)
            
        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}")
            return JSONResponse({"status": "error", "detail": str(e)})
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Обрабатывает текстовое сообщение."""
        chat_id = data.get("chat", {}).get("id")
        user_id = data.get("from", {}).get("id")
        text = data.get("text", "").strip()
        
        if not chat_id:
            return JSONResponse({"status": "error", "detail": "No chat_id"})
        
        # Проверяем, зарегистрирован ли пользователь
        user_data = self.user_repo.load_user_data(str(chat_id))
        
        # Проверяем состояние сессии
        session = self.user_sessions.get(chat_id, {})
        step = session.get("step")
        
        if step:
            # Продолжаем сбор данных
            return await self._handle_data_collection(chat_id, text, session)
        
        # Если пользователь есть - показываем меню
        if user_data:
            welcome = f"👋 С возвращением, {user_data.get('first_name')}!\n\nВыберите действие:"
            await self.max_api.send_message(chat_id, welcome, get_main_menu_keyboard())
        else:
            # Начинаем регистрацию
            await self._start_registration(chat_id)
        
        return JSONResponse({"status": "ok"})
    
    async def _handle_callback(self, data: Dict[str, Any]):
        """Обрабатывает callback запрос."""
        callback = data.get("callback_query", {})
        callback_id = callback.get("id")
        chat_id = callback.get("message", {}).get("chat", {}).get("id")
        message_id = callback.get("message", {}).get("message_id")
        data = callback.get("data", "")
        
        if not chat_id:
            return JSONResponse({"status": "error", "detail": "No chat_id"})
        
        # Отвечаем на callback
        await self.max_api.answer_callback_query(callback_id)
        
        # Обрабатываем действие
        if data == "cancel":
            await self._cancel_action(chat_id, message_id)
        
        elif data == "skip":
            await self._handle_skip(chat_id, message_id)
        
        elif data == "back":
            await self._show_menu(chat_id, message_id)
        
        elif data == "help":
            await self._show_help(chat_id, message_id)
        
        elif data == "update_data":
            await self._start_registration(chat_id, message_id)
        
        elif data == "natal":
            await self._show_natal(chat_id, message_id)
        
        elif data == "daily":
            await self._show_daily_forecast(chat_id, message_id)
        
        elif data == "solar":
            await self._show_solar(chat_id, message_id)
        
        elif data == "synastry":
            await self._show_synastry(chat_id, message_id)
        
        elif data == "report":
            await self._show_report(chat_id, message_id)
        
        elif data in ["first_name", "last_name", "birth_date", "birth_time", "place"]:
            await self._handle_data_step(chat_id, message_id, data)
        
        else:
            # Неизвестный callback
            await self.max_api.send_message(chat_id, "⚠️ Неизвестная команда", get_back_keyboard())
        
        return JSONResponse({"status": "ok"})
    
    # ==================== Регистрация ====================
    
    async def _start_registration(self, chat_id: str, message_id: Optional[str] = None):
        """Начинает процесс регистрации."""
        session = {
            "step": "first_name",
            "data": {
                "chat_id": chat_id
            }
        }
        self.user_sessions[chat_id] = session
        
        text = "👋 Привет! Я астрологический бот.\n\nДавай создадим твою натальную карту!\n\n📝 Как тебя зовут?"
        
        if message_id:
            await self.max_api.edit_message_text(chat_id, message_id, text, get_cancel_keyboard())
        else:
            await self.max_api.send_message(chat_id, text, get_cancel_keyboard())
    
    async def _handle_data_collection(self, chat_id: str, text: str, session: Dict[str, Any]):
        """Обрабатывает ввод данных при регистрации."""
        step = session.get("step")
        data = session.get("data", {})
        
        if step == "first_name":
            if not text:
                await self.max_api.send_message(chat_id, "❌ Имя не может быть пустым. Попробуйте снова:")
                return
            
            data["first_name"] = text
            session["step"] = "last_name"
            session["data"] = data
            
            await self.max_api.send_message(
                chat_id,
                f"Приятно познакомиться, {text}! 👋\n\nТеперь скажи свою фамилию (или нажми 'Пропустить'):",
                get_skip_keyboard()
            )
        
        elif step == "last_name":
            if text.lower() != "пропустить":
                data["last_name"] = text
            session["step"] = "birth_date"
            session["data"] = data
            
            await self.max_api.send_message(
                chat_id,
                "📅 Отлично! Теперь напиши дату рождения в формате **ДД-ММ-ГГГГ**\n\nНапример: 25-11-1986",
                get_cancel_keyboard()
            )
        
        elif step == "birth_date":
            try:
                datetime.strptime(text, "%d-%m-%Y")
                data["birth_date"] = text
                session["step"] = "birth_time"
                session["data"] = data
                
                await self.max_api.send_message(
                    chat_id,
                    "⏰ Принято! Теперь напиши время рождения в формате **ЧЧ-ММ**\n\nНапример: 06-10",
                    get_cancel_keyboard()
                )
            except ValueError:
                await self.max_api.send_message(
                    chat_id,
                    "❌ Неверный формат! Используй **ДД-ММ-ГГГГ** (например: 25-11-1986)"
                )
        
        elif step == "birth_time":
            try:
                h, m = map(int, text.split('-'))
                if 0 <= h <= 23 and 0 <= m <= 59:
                    data["birth_time"] = text
                    session["step"] = "place"
                    session["data"] = data
                    
                    await self.max_api.send_message(
                        chat_id,
                        "📍 Отлично! Теперь напиши город рождения:",
                        get_cancel_keyboard()
                    )
                else:
                    await self.max_api.send_message(
                        chat_id,
                        "❌ Часы должны быть 0-23, минуты 0-59. Попробуй снова:"
                    )
            except ValueError:
                await self.max_api.send_message(
                    chat_id,
                    "❌ Неверный формат! Используй **ЧЧ-ММ** (например: 06-10)"
                )
        
        elif step == "place":
            if not text:
                await self.max_api.send_message(chat_id, "❌ Город не может быть пустым. Попробуй снова:")
                return
            
            data["place"] = text
            session["data"] = data
            
            # Завершаем регистрацию
            await self._complete_registration(chat_id, data)
    
    async def _handle_skip(self, chat_id: str, message_id: str):
        """Обрабатывает пропуск поля."""
        session = self.user_sessions.get(chat_id, {})
        step = session.get("step")
        
        if step == "last_name":
            session["step"] = "birth_date"
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "📅 Отлично! Теперь напиши дату рождения в формате **ДД-ММ-ГГГГ**\n\nНапример: 25-11-1986",
                get_cancel_keyboard()
            )
    
    async def _cancel_action(self, chat_id: str, message_id: str):
        """Отменяет текущее действие."""
        if chat_id in self.user_sessions:
            del self.user_sessions[chat_id]
        
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            "❌ Действие отменено.\n\nВыберите действие из меню:",
            get_main_menu_keyboard()
        )
    
    async def _complete_registration(self, chat_id: str, data: Dict[str, Any]):
        """Завершает регистрацию пользователя."""
        # Генерируем username
        username = self.user_repo.generate_username(
            data.get("first_name", ""),
            data.get("last_name")
        )
        data["username"] = username
        data["chat_id"] = chat_id
        
        # Сохраняем
        self.user_repo.save_user_data(username, data)
        
        # Очищаем сессию
        if chat_id in self.user_sessions:
            del self.user_sessions[chat_id]
        
        # Подтверждение
        response = f"✅ {data.get('first_name')}, твои данные сохранены!\n\n"
        response += f"📝 Имя: {data.get('first_name')}\n"
        response += f"📝 Фамилия: {data.get('last_name') or 'Не указана'}\n"
        response += f"📅 Дата рождения: {data.get('birth_date')}\n"
        response += f"⏰ Время рождения: {data.get('birth_time')}\n"
        response += f"📍 Город: {data.get('place')}\n\n"
        response += "Теперь я могу рассчитать твою натальную карту! 🧙‍♂️\n\n"
        response += "Выбери действие:"
        
        await self.max_api.send_message(chat_id, response, get_main_menu_keyboard())
    
    # ==================== Меню ====================
    
    async def _show_menu(self, chat_id: str, message_id: str):
        """Показывает главное меню."""
        user_data = self.user_repo.load_user_data(str(chat_id))
        if not user_data:
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "⚠️ Данные не найдены. Пожалуйста, пройдите регистрацию.",
                get_cancel_keyboard()
            )
            return
        
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            f"👋 Главное меню, {user_data.get('first_name')}!\n\nВыбери действие:",
            get_main_menu_keyboard()
        )
    
    async def _show_help(self, chat_id: str, message_id: str):
        """Показывает помощь."""
        help_text = """
🤖 **Астрологический бот**

Доступные функции:

📊 **Натальная карта** — расчет твоей карты рождения
🔮 **Ежедневный прогноз** — транзиты на сегодня
🌞 **Солярное возвращение** — годовой прогноз
💑 **Совместимость** — сравнение с партнером
📄 **Полный отчет** — детальный анализ

Для использования функций тебе нужно:
1. Зарегистрироваться (ввести данные рождения)
2. Выбрать нужную функцию из меню

Все данные хранятся в безопасности на сервере.
"""
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            help_text,
            get_back_keyboard()
        )
    
    # ==================== Натальная карта ====================
    
    async def _show_natal(self, chat_id: str, message_id: str):
        """Показывает натальную карту."""
        user_data = self.user_repo.load_user_data(str(chat_id))
        if not user_data:
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "⚠️ Данные не найдены. Пожалуйста, пройдите регистрацию.",
                get_cancel_keyboard()
            )
            return
        
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            "🧐 Рассчитываю натальную карту...",
            get_cancel_keyboard()
        )
        
        try:
            # Рассчитываем карту
            chart_data = NatalCalculator.calculate(user_data)
            
            # Сохраняем
            user_dir = user_repo.get_user_dir(user_data["username"])
            chart_file = user_dir / f"{user_data['username']}_natal.json"
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, indent=4, ensure_ascii=False, default=str)
            
            # Генерируем изображение
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            image_path = ChartDrawer.generate_chart_image(
                subject=subject,
                username=user_data["username"],
                output_dir=user_dir,
                width=800,
                height=800
            )
            
            # Формируем ответ
            response = f"📊 **Натальная карта для {user_data.get('first_name')}**\n\n"
            response += f"🌅 Асцендент: {chart_data['chart']['ascendant']['sign']} ({chart_data['chart']['ascendant']['degree']}°)\n"
            response += f"🪐 Планет: {len(chart_data['chart']['positions'])}\n"
            response += f"⚡ Аспектов: {len(chart_data['chart']['aspects'])}\n\n"
            
            response += "📊 **Стихии:**\n"
            elements = chart_data.get('elements', {})
            response += f"🔥 Огонь: {elements.get('fire', 0):.1f}%\n"
            response += f"🌍 Земля: {elements.get('earth', 0):.1f}%\n"
            response += f"💨 Воздух: {elements.get('air', 0):.1f}%\n"
            response += f"💧 Вода: {elements.get('water', 0):.1f}%\n"
            
            response += "\n📊 **Качества:**\n"
            qualities = chart_data.get('qualities', {})
            response += f"🔵 Кардинальные: {qualities.get('cardinal', 0):.1f}%\n"
            response += f"🟢 Фиксированные: {qualities.get('fixed', 0):.1f}%\n"
            response += f"🟡 Мутабельные: {qualities.get('mutable', 0):.1f}%\n"
            
            if image_path and Path(image_path).exists():
                # Отправляем изображение
                await self.max_api.send_photo(
                    chat_id,
                    str(image_path),
                    response
                )
            else:
                # Отправляем только текст
                await self.max_api.send_message(
                    chat_id,
                    response,
                    get_back_keyboard()
                )
                
        except Exception as e:
            logger.error(f"Ошибка расчета натальной карты: {e}")
            await self.max_api.send_message(
                chat_id,
                f"❌ Ошибка: {str(e)}\n\nПопробуйте позже.",
                get_back_keyboard()
            )
    
    # ==================== Ежедневный прогноз ====================
    
    async def _show_daily_forecast(self, chat_id: str, message_id: str):
        """Показывает ежедневный прогноз."""
        user_data = self.user_repo.load_user_data(str(chat_id))
        if not user_data:
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "⚠️ Данные не найдены. Пожалуйста, пройдите регистрацию.",
                get_cancel_keyboard()
            )
            return
        
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            "🔮 Рассчитываю ежедневный прогноз...",
            get_cancel_keyboard()
        )
        
        try:
            transits = TransitsCalculator.calculate_current_transits(
                user_data=user_data,
                min_significance=2
            )
            
            response = f"🔮 **Ежедневный прогноз для {user_data.get('first_name')}**\n\n"
            response += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
            response += f"⭐ **Оценка дня:** {transits['day_score']['overall']} ({transits['day_score']['level']})\n"
            response += f"📝 {transits['summary']}\n\n"
            
            if transits['aspects']['list']:
                response += "📊 **Значимые транзиты:**\n"
                for aspect in transits['aspects']['list'][:5]:
                    response += f"• {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)\n"
            
            if transits['aspects']['total_all'] > 5:
                response += f"\n... и еще {transits['aspects']['total_all'] - 5} аспектов"
            
            await self.max_api.send_message(
                chat_id,
                response,
                get_back_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка расчета прогноза: {e}")
            await self.max_api.send_message(
                chat_id,
                f"❌ Ошибка: {str(e)}\n\nПопробуйте позже.",
                get_back_keyboard()
            )
    
    # ==================== Солярное возвращение ====================
    
    async def _show_solar(self, chat_id: str, message_id: str):
        """Показывает солярное возвращение."""
        user_data = self.user_repo.load_user_data(str(chat_id))
        if not user_data:
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "⚠️ Данные не найдены. Пожалуйста, пройдите регистрацию.",
                get_cancel_keyboard()
            )
            return
        
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            "🌞 Рассчитываю солярное возвращение...",
            get_cancel_keyboard()
        )
        
        try:
            next_year = datetime.now().year + 1
            
            solar = ReturnsCalculator.calculate_solar_return(
                user_data=user_data,
                year=next_year,
                city=user_data.get('place', 'Current Location')
            )
            
            response = f"🌞 **Солярное возвращение на {next_year} год**\n\n"
            response += f"📅 Дата: {solar['return_date']}\n"
            response += f"🌅 Асцендент: {solar['ascendant']['sign']} ({solar['ascendant']['degree']}°)\n"
            response += f"⚡ Аспектов: {solar['aspects']['total']}\n\n"
            response += f"📝 **Прогноз на год:**\n{solar['summary']}\n\n"
            
            if solar['aspects']['list']:
                response += "📊 **Основные аспекты:**\n"
                for aspect in solar['aspects']['list'][:5]:
                    response += f"• {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)\n"
            
            await self.max_api.send_message(
                chat_id,
                response,
                get_back_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка расчета солярного возвращения: {e}")
            await self.max_api.send_message(
                chat_id,
                f"❌ Ошибка: {str(e)}\n\nПопробуйте позже.",
                get_back_keyboard()
            )
    
    # ==================== Синастрия ====================
    
    async def _show_synastry(self, chat_id: str, message_id: str):
        """Показывает интерфейс для синастрии."""
        user_data = self.user_repo.load_user_data(str(chat_id))
        if not user_data:
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "⚠️ Данные не найдены. Пожалуйста, пройдите регистрацию.",
                get_cancel_keyboard()
            )
            return
        
        # Здесь можно реализовать выбор второго пользователя
        # Пока просто показываем демо-версию
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            "💑 **Совместимость (Синастрия)**\n\n"
            "Функция в разработке. Чтобы использовать совместимость, "
            "нужно будет ввести username второго пользователя.\n\n"
            "Пока можно попробовать демо-версию:",
            get_back_keyboard()
        )
    
    # ==================== Полный отчет ====================
    
    async def _show_report(self, chat_id: str, message_id: str):
        """Показывает полный отчет."""
        user_data = self.user_repo.load_user_data(str(chat_id))
        if not user_data:
            await self.max_api.edit_message_text(
                chat_id,
                message_id,
                "⚠️ Данные не найдены. Пожалуйста, пройдите регистрацию.",
                get_cancel_keyboard()
            )
            return
        
        await self.max_api.edit_message_text(
            chat_id,
            message_id,
            "📄 Генерирую полный отчет...",
            get_cancel_keyboard()
        )
        
        try:
            # 1. Натальная карта
            chart_data = NatalCalculator.calculate(user_data)
            
            # 2. Аспекты
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            aspects = AspectsCalculator.calculate_single_chart_aspects(subject)
            
            # 3. Текущие транзиты
            transits = TransitsCalculator.calculate_current_transits(user_data)
            
            # 4. Солярное возвращение
            next_year = datetime.now().year + 1
            solar = ReturnsCalculator.calculate_solar_return(
                user_data=user_data,
                year=next_year,
                city=user_data.get('place', 'Current Location')
            )
            
            # Формируем отчет
            response = f"📄 **Полный астрологический отчет для {user_data.get('first_name')}**\n\n"
            
            response += "📊 **Натальная карта**\n"
            response += f"• Планет: {len(chart_data['chart']['positions'])}\n"
            response += f"• Домов: {len(chart_data['chart']['houses'])}\n"
            response += f"• Аспектов: {len(chart_data['chart']['aspects'])}\n"
            response += f"• Асцендент: {chart_data['chart']['ascendant']['sign']} ({chart_data['chart']['ascendant']['degree']}°)\n\n"
            
            elements = chart_data.get('elements', {})
            response += "**Стихии:** "
            response += f"🔥{elements.get('fire', 0):.0f}% "
            response += f"🌍{elements.get('earth', 0):.0f}% "
            response += f"💨{elements.get('air', 0):.0f}% "
            response += f"💧{elements.get('water', 0):.0f}%\n\n"
            
            response += "🔮 **Транзиты на сегодня**\n"
            response += f"• Оценка: {transits['day_score']['overall']} ({transits['day_score']['level']})\n"
            response += f"• {transits['summary']}\n\n"
            
            response += "🌞 **Солярное возвращение на {next_year}**\n"
            response += f"• {solar['summary']}\n"
            
            # Сохраняем отчет
            user_dir = user_repo.get_user_dir(user_data["username"])
            report_file = user_dir / f"{user_data['username']}_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            await self.max_api.send_message(
                chat_id,
                response,
                get_back_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            await self.max_api.send_message(
                chat_id,
                f"❌ Ошибка: {str(e)}\n\nПопробуйте позже.",
                get_back_keyboard()
            )
    
    async def _handle_data_step(self, chat_id: str, message_id: str, data: str):
        """Обрабатывает шаги сбора данных."""
        # Здесь можно реализовать редактирование данных
        pass


# ==================== Webhook эндпоинт ====================

bot = AstrologyBot()

@app.post("/webhook")
async def webhook(request: Request):
    """Эндпоинт для вебхука от MAX."""
    return await bot.handle_webhook(request)


# ==================== Тестовый эндпоинт ====================

@app.get("/test")
async def test():
    """Тестовый эндпоинт для проверки работы бота."""
    return {
        "status": "ok",
        "message": "Бот работает",
        "timestamp": datetime.now().isoformat()
    }


# ==================== Запуск ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Астрологический бот для MAX")
    print("=" * 60)
    print(f"\n📡 Сервер запущен на http://{Config.HOST}:{Config.PORT}")
    print(f"📚 Документация: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"🔗 Webhook URL: http://{Config.HOST}:{Config.PORT}/webhook")
    print("\n⚠️ Для работы с MAX необходимо:")
    print("   1. Заменить MAX_BOT_TOKEN на реальный токен")
    print("   2. Задеплоить на публичный сервер с HTTPS")
    print("   3. Зарегистрировать вебхук в MAX Bot API")
    print("\n" + "=" * 60)
    
    uvicorn.run(
        "max_bot:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )