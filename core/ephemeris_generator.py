"""
Модуль для генерации эфемерид (временных рядов астрологических данных)

Эфемериды — это таблицы положений планет на определенные даты и время.
Модуль позволяет:
1. Генерировать эфемериды на период (дни, часы, минуты)
2. Сохранять данные в структурированном JSON формате
3. Использовать для транзитов, прогрессий и других прогнозов

Эфемериды используются для:
- Транзитного анализа (сравнение с натальной картой)
- Прогнозирования событий
- Анализа планетарных циклов
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

from kerykeion import EphemerisDataFactory

from core.subject_factory import SubjectFactory
from core.exceptions import EphemerisGenerationError

logger = logging.getLogger(__name__)


class EphemerisGenerator:
    """
    Генератор эфемерид для астрологических расчетов.
    """
    
    # Планеты для включения в эфемериды
    PLANETS = [
        "sun", "moon", "mercury", "venus", "mars",
        "jupiter", "saturn", "uranus", "neptune", "pluto",
        "chiron", "lilith", "true_north_lunar_node"
    ]
    
    @classmethod
    def generate_daily_ephemeris(
        cls,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        latitude: float = 47.2357,
        longitude: float = 39.7015,
        timezone: str = "Europe/Moscow",
        include_houses: bool = False
    ) -> Dict[str, Any]:
        """
        Генерирует ежедневные эфемериды за период.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            latitude: Широта для расчета домов
            longitude: Долгота для расчета домов
            timezone: Часовой пояс
            include_houses: Включать ли данные домов
            
        Returns:
            Dict: Данные эфемерид
        """
        try:
            # Преобразуем даты
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            logger.info(f"Генерация ежедневных эфемерид с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")
            
            # Создаем фабрику эфемерид
            factory = EphemerisDataFactory(
                start_datetime=start_date,
                end_datetime=end_date,
                step_type="days",
                step=1,
                lat=latitude,
                lng=longitude,
                tz_str=timezone
            )
            
            # Получаем данные
            if include_houses:
                ephemeris_data = factory.get_ephemeris_data_as_astrological_subjects()
                data = cls._format_subjects_data(ephemeris_data, start_date, end_date)
            else:
                ephemeris_data = factory.get_ephemeris_data()
                data = cls._format_dict_data(ephemeris_data, start_date, end_date)
            
            logger.info(f"Эфемериды сгенерированы. Дней: {len(data['days'])}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации эфемерид: {e}")
            raise EphemerisGenerationError(f"Не удалось сгенерировать эфемериды: {e}")
    
    @classmethod
    def generate_hourly_ephemeris(
        cls,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        latitude: float = 47.2357,
        longitude: float = 39.7015,
        timezone: str = "Europe/Moscow",
        step_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Генерирует почасовые эфемериды за период.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            latitude: Широта
            longitude: Долгота
            timezone: Часовой пояс
            step_hours: Шаг в часах
            
        Returns:
            Dict: Данные эфемерид
        """
        try:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            logger.info(f"Генерация почасовых эфемерид с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")
            
            factory = EphemerisDataFactory(
                start_datetime=start_date,
                end_datetime=end_date,
                step_type="hours",
                step=step_hours,
                lat=latitude,
                lng=longitude,
                tz_str=timezone
            )
            
            ephemeris_data = factory.get_ephemeris_data()
            data = cls._format_dict_data(ephemeris_data, start_date, end_date)
            
            logger.info(f"Почасовые эфемериды сгенерированы. Точек: {len(data['days'])}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации почасовых эфемерид: {e}")
            raise EphemerisGenerationError(f"Не удалось сгенерировать почасовые эфемериды: {e}")
    
    @classmethod
    def generate_ephemeris_for_date_range(
        cls,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        step_type: str = "days",
        step: int = 1,
        latitude: float = 47.2357,
        longitude: float = 39.7015,
        timezone: str = "Europe/Moscow"
    ) -> Dict[str, Any]:
        """
        Генерирует эфемериды с гибкими настройками шага.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            step_type: Тип шага ("days", "hours", "minutes")
            step: Шаг
            latitude: Широта
            longitude: Долгота
            timezone: Часовой пояс
            
        Returns:
            Dict: Данные эфемерид
        """
        try:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            logger.info(f"Генерация эфемерид ({step_type}, шаг {step}) с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")
            
            factory = EphemerisDataFactory(
                start_datetime=start_date,
                end_datetime=end_date,
                step_type=step_type,
                step=step,
                lat=latitude,
                lng=longitude,
                tz_str=timezone
            )
            
            ephemeris_data = factory.get_ephemeris_data()
            data = cls._format_dict_data(ephemeris_data, start_date, end_date)
            
            logger.info(f"Эфемериды сгенерированы. Точек: {len(data['days'])}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка генерации эфемерид: {e}")
            raise EphemerisGenerationError(f"Не удалось сгенерировать эфемериды: {e}")
    
    @classmethod
    def get_planet_positions_on_date(
        cls,
        target_date: Union[str, datetime],
        latitude: float = 47.2357,
        longitude: float = 39.7015,
        timezone: str = "Europe/Moscow"
    ) -> Dict[str, Any]:
        """
        Получает положения планет на конкретную дату.
        
        Args:
            target_date: Дата для расчета
            latitude: Широта
            longitude: Долгота
            timezone: Часовой пояс
            
        Returns:
            Dict: Положения планет на указанную дату
        """
        try:
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, "%Y-%m-%d")
            
            # Создаем субъект на указанную дату
            subject = SubjectFactory.create_subject(
                name=f"Ephemeris {target_date.strftime('%Y-%m-%d')}",
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
                hour=12,
                minute=0,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone
            )
            
            # Извлекаем положения планет
            positions = {}
            for planet_name in cls.PLANETS:
                planet = getattr(subject, planet_name, None)
                if planet is not None:
                    display_name = planet_name.replace('_', ' ').title()
                    if planet_name == "true_north_lunar_node":
                        display_name = "North Node"
                    elif planet_name == "lilith":
                        display_name = "Lilith"
                    
                    sign = getattr(planet, 'sign', 'Unknown')
                    if hasattr(sign, 'sign'):
                        sign = sign.sign
                    
                    positions[display_name] = {
                        "sign": str(sign),
                        "degree": round(getattr(planet, 'position', 0), 2),
                        "abs_pos": round(getattr(planet, 'abs_pos', 0), 2),
                        "retrograde": getattr(planet, 'retrograde', False)
                    }
            
            return {
                "date": target_date.isoformat(),
                "positions": positions,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения положений планет на дату: {e}")
            raise EphemerisGenerationError(f"Не удалось получить положения планет: {e}")
    
    @classmethod
    def _format_dict_data(
        cls,
        ephemeris_data: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Форматирует данные эфемерид из словарей.
        """
        days_data = []
        
        for entry in ephemeris_data:
            day_info = {
                "date": entry.get("date", ""),
                "planets": []
            }
            
            # Извлекаем планеты
            for planet in entry.get("planets", []):
                day_info["planets"].append({
                    "name": planet.get("name", ""),
                    "sign": planet.get("sign", ""),
                    "degree": round(planet.get("position", 0), 2),
                    "abs_pos": round(planet.get("abs_pos", 0), 2),
                    "retrograde": planet.get("retrograde", False)
                })
            
            days_data.append(day_info)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "step_type": "days",
                "step": 1,
                "total_days": len(days_data)
            },
            "days": days_data
        }
    
    @classmethod
    def _format_subjects_data(
        cls,
        ephemeris_data: List,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Форматирует данные эфемерид из объектов AstrologicalSubject.
        """
        days_data = []
        
        for subject in ephemeris_data:
            day_info = {
                "date": getattr(subject, 'iso_formatted_local_datetime', str(start_date)),
                "planets": []
            }
            
            for planet_name in cls.PLANETS:
                planet = getattr(subject, planet_name, None)
                if planet is not None:
                    sign = getattr(planet, 'sign', 'Unknown')
                    if hasattr(sign, 'sign'):
                        sign = sign.sign
                    
                    day_info["planets"].append({
                        "name": planet_name.capitalize(),
                        "sign": str(sign),
                        "degree": round(getattr(planet, 'position', 0), 2),
                        "abs_pos": round(getattr(planet, 'abs_pos', 0), 2),
                        "retrograde": getattr(planet, 'retrograde', False)
                    })
            
            days_data.append(day_info)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "step_type": "days",
                "step": 1,
                "total_days": len(days_data)
            },
            "days": days_data
        }
    
    @classmethod
    def save_ephemeris_to_file(
        cls,
        ephemeris_data: Dict[str, Any],
        filename: str,
        output_dir: Path
    ) -> Path:
        """
        Сохраняет эфемериды в JSON файл.
        
        Args:
            ephemeris_data: Данные эфемерид
            filename: Имя файла
            output_dir: Папка для сохранения
            
        Returns:
            Path: Путь к сохраненному файлу
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ephemeris_data, f, indent=4, ensure_ascii=False, default=str)
        
        logger.info(f"Эфемериды сохранены в: {file_path}")
        return file_path