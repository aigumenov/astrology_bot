"""
Модуль для создания астрологических субъектов
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from kerykeion import AstrologicalSubject

from core.exceptions import SubjectCreationError

logger = logging.getLogger(__name__)


class SubjectFactory:
    """
    Фабрика для создания астрологических субъектов.
    Инкапсулирует создание AstrologicalSubject с предварительной настройкой.
    """
    
    DEFAULT_TIMEZONE = "Europe/Moscow"
    DEFAULT_LATITUDE = 47.2357  # Ростов-на-Дону
    DEFAULT_LONGITUDE = 39.7015
    
    @classmethod
    def create_subject(
        cls,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        latitude: float,
        longitude: float,
        timezone: str = DEFAULT_TIMEZONE,
        **kwargs
    ) -> AstrologicalSubject:
        """
        Создает AstrologicalSubject из переданных данных.
        
        Args:
            name: Имя субъекта
            year, month, day: Дата рождения
            hour, minute: Время рождения
            latitude, longitude: Координаты места рождения
            timezone: Часовой пояс
            **kwargs: Дополнительные параметры (zodiac_type, houses_system, etc.)
            
        Returns:
            AstrologicalSubject: Созданный субъект
            
        Raises:
            SubjectCreationError: Если не удалось создать субъект
        """
        try:
            logger.info(f"Создание субъекта: {name} ({day}-{month}-{year} {hour}:{minute})")
            
            subject = AstrologicalSubject(
                name=name,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                lat=latitude,
                lng=longitude,
                tz_str=timezone,
                online=False,  # Используем офлайн режим с координатами
                **kwargs
            )
            
            logger.info(f"Субъект {name} создан успешно")
            return subject
            
        except Exception as e:
            logger.error(f"Ошибка создания субъекта {name}: {e}")
            raise SubjectCreationError(f"Не удалось создать субъект: {e}")
    
    @classmethod
    def create_subject_from_user_data(
        cls,
        user_data: Dict[str, Any]
    ) -> AstrologicalSubject:
        """
        Создает AstrologicalSubject из данных пользователя.
        
        Args:
            user_data: Словарь с данными пользователя (из JSON)
            
        Returns:
            AstrologicalSubject: Созданный субъект
        """
        # Парсим дату рождения
        birth_date = datetime.strptime(user_data['birth_date'], "%d-%m-%Y")
        hour, minute = map(int, user_data['birth_time'].split('-'))
        
        # Получаем координаты
        latitude = user_data.get('latitude', cls.DEFAULT_LATITUDE)
        longitude = user_data.get('longitude', cls.DEFAULT_LONGITUDE)
        timezone = user_data.get('timezone', cls.DEFAULT_TIMEZONE)
        
        # Формируем имя
        name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        if not name:
            name = user_data.get('username', 'User')
        
        return cls.create_subject(
            name=name,
            year=birth_date.year,
            month=birth_date.month,
            day=birth_date.day,
            hour=hour,
            minute=minute,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
    
    @classmethod
    def create_transit_subject(
        cls,
        name: str = "Current Transits",
        latitude: float = DEFAULT_LATITUDE,
        longitude: float = DEFAULT_LONGITUDE,
        timezone: str = DEFAULT_TIMEZONE,
    ) -> AstrologicalSubject:
        """
        Создает субъект для текущего времени (транзиты).
        
        Args:
            name: Имя субъекта
            latitude, longitude: Координаты места
            timezone: Часовой пояс
            
        Returns:
            AstrologicalSubject: Субъект для текущего времени
        """
        now = datetime.now()
        
        return cls.create_subject(
            name=name,
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )