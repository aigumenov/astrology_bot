#!/usr/bin/env python3
"""
FastAPI сервер для астрологического бота
Предоставляет REST API для всех астрологических модулей

Запуск:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload

Документация:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

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

def error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Форматирует ответ с ошибкой."""
    return {
        "status": "error",
        "message": message
    }

# ==================== Эндпоинты ====================

@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "service": "Астрологический бот API",
        "version": "1.0.0",
        "endpoints": {
            "/docs": "Документация Swagger",
            "/redoc": "Документация ReDoc",
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


# ==================== Пользователи ====================

@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserData):
    """
    Создает нового пользователя.
    """
    try:
        # Генерируем username
        username = user_repo.generate_username(user_data.first_name, user_data.last_name)
        
        # Формируем данные
        data = user_data.dict()
        data["username"] = username
        
        # Сохраняем
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
    """
    Получает данные пользователя.
    """
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
    """
    Список всех пользователей.
    """
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


@app.delete("/users/{username}")
async def delete_user(username: str):
    """
    Удаляет пользователя.
    """
    try:
        user_dir = user_repo.get_user_dir(username)
        if not user_dir.exists():
            raise HTTPException(status_code=404, detail=f"Пользователь {username} не найден")
        
        # Удаляем папку со всем содержимым
        import shutil
        shutil.rmtree(user_dir)
        
        return format_response(None, f"Пользователь {username} удален")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления пользователя: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Натальная карта ====================

@app.post("/natal")
async def calculate_natal(request: NatalRequest):
    """
    Рассчитывает натальную карту.
    """
    try:
        user_data = load_user(request.username)
        
        # Рассчитываем карту
        chart_data = NatalCalculator.calculate(user_data)
        
        # Сохраняем если нужно
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
    """
    Рассчитывает транзиты.
    """
    try:
        user_data = load_user(request.username)
        
        if request.days > 1:
            # Период транзитов
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
            # Текущие транзиты
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
    """
    Рассчитывает синастрию (совместимость).
    """
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
    """
    Рассчитывает солярное возвращение.
    """
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
    """
    Рассчитывает лунное возвращение.
    """
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
    """
    Генерирует эфемериды.
    """
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
    """
    Генерирует изображение натальной карты.
    """
    try:
        user_data = load_user(request.username)
        
        # Создаем субъект
        subject = SubjectFactory.create_subject_from_user_data(user_data)
        
        # Генерируем изображение
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


@app.get("/static/{username}/{filename}")
async def serve_static(username: str, filename: str):
    """
    Возвращает статический файл (изображение).
    """
    user_dir = user_repo.get_user_dir(username)
    file_path = user_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path)


# ==================== Полный отчет ====================

@app.post("/report")
async def generate_report(request: ReportRequest):
    """
    Генерирует полный отчет по пользователю.
    """
    try:
        user_data = load_user(request.username)
        
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
        
        # Сохраняем отчет
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


# ==================== Запуск ====================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )