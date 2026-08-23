#!/usr/bin/env python3
"""
FastAPI сервер для астрологического бота
Адаптирован для работы на Bothost
"""

import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from pydantic import BaseModel, Field
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

# Инициализация репозитория
user_repo = UserRepository()

# ==================== Конфигурация MAX API ====================

# Получаем токен из переменных окружения
MAX_BOT_TOKEN = os.environ.get("MAX_BOT_TOKEN")

# Если токен не найден или пустой, используем fallback
if not MAX_BOT_TOKEN:
    MAX_BOT_TOKEN = "f9LHodD0cOI7akoq3U7PCyihj1qMFmDjRtDKVoIxhtz99oOOHCEkZfey_KnSzJi4gdtbiU9TgtjD5CDbwAVH"
    logger.warning("⚠️ Токен загружен из fallback-значения (не из переменных окружения)")

MAX_API_URL = "https://platform-api2.max.ru"

logger.info(f"🔑 Токен загружен: {MAX_BOT_TOKEN[:20]}...")



# ==================== Pydantic модели ====================

class UserData(BaseModel):
    """Модель данных пользователя."""
    first_name: str = Field(..., description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    birth_date: str = Field(..., description="Дата рождения (ДД-ММ-ГГГГ)")
    birth_time: str = Field(..., description="Время рождения (ЧЧ-ММ)")
    place: str = Field(..., description="Город рождения")
    latitude: float = Field(47.2357, description="Широта")
    longitude: float = Field(39.7015, description="Долгота")
    timezone: str = Field("Europe/Moscow", description="Часовой пояс")

class UserResponse(BaseModel):
    """Модель ответа для пользователя."""
    username: str
    message: str
    data: Optional[Dict[str, Any]] = None

class NatalRequest(BaseModel):
    """Запрос на расчет натальной карты."""
    username: str = Field(..., description="Имя пользователя")
    save: bool = Field(False, description="Сохранить результат")

class TransitsRequest(BaseModel):
    """Запрос на расчет транзитов."""
    username: str = Field(..., description="Имя пользователя")
    days: int = Field(1, description="Количество дней (1 для текущих)")
    significance: int = Field(2, description="Минимальная значимость (1-5)")

class SynastryRequest(BaseModel):
    """Запрос на расчет синастрии."""
    user1: str = Field(..., description="Имя первого пользователя")
    user2: str = Field(..., description="Имя второго пользователя")
    minor: bool = Field(False, description="Включить второстепенные аспекты")
    significance: int = Field(2, description="Минимальная значимость (1-5)")

class SolarRequest(BaseModel):
    """Запрос на расчет солярного возвращения."""
    username: str = Field(..., description="Имя пользователя")
    year: Optional[int] = Field(None, description="Год для расчета")
    city: Optional[str] = Field(None, description="Город для возвращения")

class LunarRequest(BaseModel):
    """Запрос на расчет лунного возвращения."""
    username: str = Field(..., description="Имя пользователя")
    city: Optional[str] = Field(None, description="Город для возвращения")

class EphemerisRequest(BaseModel):
    """Запрос на генерацию эфемерид."""
    start_date: str = Field(..., description="Начальная дата (YYYY-MM-DD)")
    end_date: str = Field(..., description="Конечная дата (YYYY-MM-DD)")
    latitude: float = Field(55.7558, description="Широта")
    longitude: float = Field(37.6173, description="Долгота")
    timezone: str = Field("Europe/Moscow", description="Часовой пояс")

class ChartRequest(BaseModel):
    """Запрос на генерацию изображения карты."""
    username: str = Field(..., description="Имя пользователя")
    width: int = Field(1000, description="Ширина PNG")
    height: int = Field(1000, description="Высота PNG")

class ReportRequest(BaseModel):
    """Запрос на генерацию отчета."""
    username: str = Field(..., description="Имя пользователя")

# ==================== FastAPI приложение ====================

app = FastAPI(
    title="Астрологический бот API",
    description="API для расчета натальных карт, транзитов, синастрии и других астрологических данных",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== Вспомогательные функции ====================

def load_user(username: str) -> Dict[str, Any]:
    """Загружает данные пользователя."""
    user_data = user_repo.load_user_data(username)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"Пользователь '{username}' не найден")
    return user_data

def format_response(data: Any, message: str = "Успешно") -> Dict[str, Any]:
    """Форматирует ответ."""
    return {
        "status": "success",
        "message": message,
        "data": data
    }

# ==================== Функции для работы с MAX API ====================

async def send_message(chat_id: str, text: str):
    """Отправляет сообщение через MAX API."""
    url = f"{MAX_API_URL}/messages"
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": chat_id,
        "text": text
    }
    
    try:
        # Логируем токен для отладки
        logger.info(f"📤 Отправка в {chat_id}: токен {MAX_BOT_TOKEN[:20]}...")
        logger.info(f"📤 URL: {url}")
        logger.info(f"📤 Headers: {headers}")
        logger.info(f"📤 Payload: {payload}")
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                logger.info(f"📤 Сообщение отправлено в {chat_id}: {text[:50]}...")
            else:
                logger.error(f"❌ Ошибка отправки: {response.status_code} - {response.text}")
            return response.json()
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        return None
    
async def send_photo(chat_id: str, photo_url: str, caption: Optional[str] = None):
    url = f"{MAX_API_URL}/messages"
    headers = {
        "Authorization": f"Bearer {MAX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": chat_id,
        "attachments": [
            {
                "type": "image",
                "payload": {
                    "url": photo_url
                }
            }
        ]
    }
    if caption:
        payload["text"] = caption
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, json=payload, headers=headers)
            logger.info(f"🖼️ Фото отправлено в {chat_id}")
            return response.json()
    except Exception as e:
        logger.error(f"❌ Ошибка отправки фото: {e}")
        return None

async def handle_command(chat_id: str, text: str):
    """Обрабатывает команды."""
    if text == "/start":
        await send_message(
            chat_id,
            "👋 Добро пожаловать!\n\n"
            "Я астрологический бот. Вот что я умею:\n"
            "/natal - рассчитать натальную карту\n"
            "/transits - ежедневный прогноз\n"
            "/solar - солярное возвращение\n"
            "/report - полный отчет\n"
            "/help - помощь"
        )
    elif text == "/help":
        await send_message(
            chat_id,
            "📚 Доступные команды:\n\n"
            "/natal - натальная карта\n"
            "/transits - транзиты на сегодня\n"
            "/solar - солярное возвращение\n"
            "/report - полный отчет\n"
            "/help - эта справка"
        )
    elif text == "/natal":
        await send_message(
            chat_id,
            "🔮 Расчет натальной карты...\n\n"
            "Сначала зарегистрируй свои данные: /register"
        )
    elif text == "/register":
        await send_message(
            chat_id,
            "📝 Давай создадим твой профиль!\n\n"
            "Напиши свое имя:"
        )
    else:
        await send_message(
            chat_id,
            f"🤔 Неизвестная команда: {text}\n"
            "Напиши /help для списка команд."
        )

async def handle_callback(chat_id: str, callback_data: str):
    """Обрабатывает callback от inline-кнопок."""
    await send_message(
        chat_id,
        f"🔘 Вы нажали кнопку: {callback_data}"
    )

# ==================== Базовые эндпоинты ====================

@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы."""
    return {
        "status": "ok",
        "message": "Астрологический бот работает",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/docs": "Документация Swagger",
            "/redoc": "Документация ReDoc",
            "/health": "Проверка состояния",
            "/webhook": "Webhook для MAX",
            "/users": "Управление пользователями",
            "/natal": "Натальная карта",
            "/transits": "Транзиты",
            "/synastry": "Синастрия",
            "/solar": "Солярное возвращение",
            "/lunar": "Лунное возвращение",
            "/ephemeris": "Эфемериды",
            "/chart": "Изображение карты",
            "/report": "Полный отчет"
        }
    }

@app.get("/health")
async def health():
    """Проверка состояния сервера."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== Webhook для MAX ====================

@app.post("/webhook")
async def max_webhook(request: Request):
    """
    Обработчик вебхука от MAX.
    Сюда MAX будет отправлять все сообщения от пользователей.
    """
    try:
        # Получаем данные от MAX
        data = await request.json()
        logger.info(f"📨 Получен webhook от MAX: {data}")
        
        # Извлекаем тип обновления
        update_type = data.get("update_type")
        
        # Обрабатываем разные типы событий
        if update_type == "bot_started":
            # Пользователь запустил бота (в т.ч. по диплинку)
            user_info = data.get("user", {})
            chat_id = data.get("chat_id")
            payload = data.get("payload")
            
            logger.info(f"👤 Бот запущен пользователем {user_info.get('name')} (ID: {user_info.get('user_id')})")
            if payload:
                logger.info(f"📎 Payload: {payload}")
            
            await send_message(
                chat_id,
                "👋 Привет! Я астрологический бот.\n\n"
                "Я помогу тебе:\n"
                "📊 Рассчитать натальную карту\n"
                "🔮 Узнать ежедневный прогноз\n"
                "🌞 Получить солярное возвращение\n"
                "💑 Проверить совместимость\n\n"
                "Для начала напиши /start"
            )
            
        elif update_type == "message_created":
            # Новое сообщение от пользователя
            message_data = data.get("message", {})
            
            # Извлекаем chat_id из sender или recipient
            sender = message_data.get("sender", {})
            recipient = message_data.get("recipient", {})
            chat_id = sender.get("user_id") or recipient.get("chat_id")
            
            # Извлекаем текст из body
            body = message_data.get("body", {})
            text = body.get("text", "")
            
            logger.info(f"💬 Сообщение от {chat_id}: {text}")
            
            if text and text.startswith("/"):
                await handle_command(chat_id, text)
            else:
                await send_message(
                    chat_id,
                    "🤔 Я не совсем понял. Напиши /help для списка доступных команд."
                )
                
        elif update_type == "callback_query":
            # Нажатие на inline-кнопку
            callback_data = data.get("data")
            chat_id = data.get("chat_id")
            logger.info(f"🔘 Нажата кнопка: {callback_data}")
            await handle_callback(chat_id, callback_data)
            
        else:
            # Другие типы событий
            logger.info(f"ℹ️ Получено событие типа: {update_type}")
        
        # Возвращаем успешный ответ MAX
        return {
            "status": "ok",
            "message": "Webhook processed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

# ==================== Пользователи ====================

@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserData):
    """Создает нового пользователя."""
    try:
        username = user_repo.generate_username(user_data.first_name, user_data.last_name)
        data = user_data.dict()
        data["username"] = username
        user_repo.save_user_data(username, data)
        
        return UserResponse(
            username=username,
            message=f"Пользователь {username} создан",
            data=data
        )
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{username}")
async def get_user(username: str):
    """Получает данные пользователя."""
    try:
        user_data = load_user(username)
        return format_response(user_data, f"Данные пользователя {username}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения пользователя: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
async def list_users():
    """Список всех пользователей."""
    try:
        user_dir = Path("data/user_data")
        users = []
        if user_dir.exists():
            for user_folder in user_dir.iterdir():
                if user_folder.is_dir():
                    user_file = user_folder / f"{user_folder.name}.json"
                    if user_file.exists():
                        try:
                            with open(user_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                users.append({
                                    "username": user_folder.name,
                                    "first_name": data.get("first_name", ""),
                                    "last_name": data.get("last_name", ""),
                                    "birth_date": data.get("birth_date", "")
                                })
                        except Exception as e:
                            logger.warning(f"Ошибка чтения {user_file}: {e}")
        
        return format_response(users, f"Найдено {len(users)} пользователей")
    except Exception as e:
        logger.error(f"Ошибка списка пользователей: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Натальная карта ====================

@app.post("/natal")
async def calculate_natal(request: NatalRequest):
    """Рассчитывает натальную карту."""
    try:
        user_data = load_user(request.username)
        chart_data = NatalCalculator.calculate(user_data)
        
        if request.save:
            user_dir = user_repo.get_user_dir(request.username)
            chart_file = user_dir / f"{request.username}_natal.json"
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, indent=4, ensure_ascii=False, default=str)
        
        return format_response(chart_data, "Натальная карта рассчитана")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка расчета натальной карты: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Транзиты ====================

@app.post("/transits")
async def calculate_transits(request: TransitsRequest):
    """Рассчитывает транзиты."""
    try:
        user_data = load_user(request.username)
        
        if request.days > 1:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=request.days)
            
            transits = TransitsCalculator.calculate_transits_period(
                user_data=user_data,
                start_date=start_date,
                end_date=end_date,
                step_days=1,
                min_significance=request.significance
            )
            
            return format_response(transits, f"Транзиты за {request.days} дней рассчитаны")
        else:
            transits = TransitsCalculator.calculate_current_transits(
                user_data=user_data,
                min_significance=request.significance
            )
            
            return format_response(transits, "Текущие транзиты рассчитаны")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка расчета транзитов: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Синастрия ====================

@app.post("/synastry")
async def calculate_synastry(request: SynastryRequest):
    """Рассчитывает синастрию."""
    try:
        user1_data = load_user(request.user1)
        user2_data = load_user(request.user2)
        
        synastry = SynastryCalculator.calculate_synastry(
            user1_data=user1_data,
            user2_data=user2_data,
            include_minor_aspects=request.minor,
            min_significance=request.significance
        )
        
        return format_response(synastry, f"Синастрия между {request.user1} и {request.user2} рассчитана")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка расчета синастрии: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Солярное возвращение ====================

@app.post("/solar")
async def calculate_solar(request: SolarRequest):
    """Рассчитывает солярное возвращение."""
    try:
        user_data = load_user(request.username)
        year = request.year or datetime.now().year + 1
        city = request.city or user_data.get('place', 'Current Location')
        
        solar = ReturnsCalculator.calculate_solar_return(
            user_data=user_data,
            year=year,
            city=city
        )
        
        return format_response(solar, f"Солярное возвращение на {year} год рассчитано")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка расчета солярного возвращения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Лунное возвращение ====================

@app.post("/lunar")
async def calculate_lunar(request: LunarRequest):
    """Рассчитывает лунное возвращение."""
    try:
        user_data = load_user(request.username)
        city = request.city or user_data.get('place', 'Current Location')
        
        lunar = ReturnsCalculator.calculate_next_lunar_return(
            user_data=user_data,
            city=city
        )
        
        return format_response(lunar, "Лунное возвращение рассчитано")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка расчета лунного возвращения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Эфемериды ====================

@app.post("/ephemeris")
async def generate_ephemeris(request: EphemerisRequest):
    """Генерирует эфемериды."""
    try:
        ephemeris = EphemerisGenerator.generate_daily_ephemeris(
            start_date=request.start_date,
            end_date=request.end_date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        return format_response(ephemeris, "Эфемериды сгенерированы")
    except Exception as e:
        logger.error(f"Ошибка генерации эфемерид: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Изображение карты ====================

@app.post("/chart")
async def generate_chart(request: ChartRequest):
    """Генерирует изображение натальной карты."""
    try:
        user_data = load_user(request.username)
        subject = SubjectFactory.create_subject_from_user_data(user_data)
        
        user_dir = user_repo.get_user_dir(request.username)
        image_path = ChartDrawer.generate_chart_image(
            subject=subject,
            username=request.username,
            output_dir=user_dir,
            width=request.width,
            height=request.height
        )
        
        if image_path and Path(image_path).exists():
            return format_response({
                "image_path": str(image_path),
                "url": f"/static/{request.username}/{Path(image_path).name}"
            }, "Изображение создано")
        else:
            raise HTTPException(status_code=500, detail="Не удалось создать изображение")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка генерации изображения: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Полный отчет ====================

@app.post("/report")
async def generate_report(request: ReportRequest):
    """Генерирует полный отчет."""
    try:
        user_data = load_user(request.username)
        
        chart_data = NatalCalculator.calculate(user_data)
        subject = SubjectFactory.create_subject_from_user_data(user_data)
        aspects = AspectsCalculator.calculate_single_chart_aspects(subject)
        transits = TransitsCalculator.calculate_current_transits(user_data)
        next_year = datetime.now().year + 1
        solar = ReturnsCalculator.calculate_solar_return(
            user_data=user_data,
            year=next_year,
            city=user_data.get('place', 'Current Location')
        )
        
        report = {
            "user": {
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name', ''),
                "birth_date": user_data.get('birth_date'),
                "birth_time": user_data.get('birth_time'),
                "place": user_data.get('place', '')
            },
            "natal_chart": {
                "planets_count": len(chart_data['chart']['positions']),
                "houses_count": len(chart_data['chart']['houses']),
                "aspects_count": len(chart_data['chart']['aspects']),
                "ascendant": chart_data['chart']['ascendant'],
                "elements": chart_data.get('elements', {}),
                "qualities": chart_data.get('qualities', {})
            },
            "aspects": aspects[:20],
            "transits": {
                "date": transits['transit_date'],
                "day_score": transits['day_score'],
                "summary": transits['summary'],
                "aspects": transits['aspects']['list'][:10]
            },
            "solar_return": {
                "year": next_year,
                "date": solar['return_date'],
                "ascendant": solar['ascendant'],
                "summary": solar['summary'],
                "aspects": solar['aspects']['list'][:10]
            }
        }
        
        user_dir = user_repo.get_user_dir(request.username)
        report_file = user_dir / f"{request.username}_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False, default=str)
        
        return format_response(report, "Отчет сгенерирован")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка генерации отчета: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Запуск для Bothost ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    
    logger.info(f"🚀 Запуск сервера на порту {port}")
    logger.info(f"📚 Документация: /docs")
    logger.info(f"🔗 Webhook: /webhook")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )