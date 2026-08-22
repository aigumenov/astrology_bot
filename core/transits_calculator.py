"""
Модуль для расчета транзитов (прогнозов)

Транзиты — это текущие положения планет в сравнении с натальной картой.
Модуль позволяет:
1. Рассчитать транзиты на текущий момент
2. Рассчитать транзиты на указанную дату
3. Получить прогноз на период (дни/недели)
4. Отфильтровать значимые транзиты

Возвращает структурированный JSON для использования в других модулях.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

from core.subject_factory import SubjectFactory
from core.aspects_calculator import AspectsCalculator
from core.exceptions import TransitCalculationError

logger = logging.getLogger(__name__)


class TransitsCalculator:
    """
    Калькулятор транзитов.
    
    Рассчитывает транзитные аспекты планет к натальной карте.
    """
    
    # Значимость аспектов для фильтрации
    ASPECT_SIGNIFICANCE = {
        'Conjunction': 5,    # Соединение - очень важное
        'Opposition': 4,     # Оппозиция - важное
        'Square': 4,         # Квадрат - важное
        'Trine': 3,          # Трин - значительное
        'Sextile': 2,        # Секстиль - умеренное
        'Quincunx': 1,       # Квинконс - слабое
        'Semi-sextile': 1,   # Полусекстиль - слабое
        'Semi-square': 2,    # Полуквадрат - умеренное
        'Sesquiquadrate': 2, # Полутораквадрат - умеренное
    }
    
    # Планеты для транзитов (внешние и быстрые)
    TRANSIT_PLANETS = [
        "Sun", "Moon", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
    ]
    
    @classmethod
    def calculate_current_transits(
        cls,
        user_data: Dict[str, Any],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        min_significance: int = 2,
        include_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает транзиты на текущий момент.
        
        Args:
            user_data: Данные пользователя
            latitude: Широта для транзитов (если None, берется из user_data)
            longitude: Долгота для транзитов (если None, берется из user_data)
            timezone: Часовой пояс
            min_significance: Минимальная значимость аспекта (1-5)
            include_aspects: Список аспектов для включения (если None - все)
            
        Returns:
            Dict: Данные о транзитах
        """
        try:
            logger.info(f"Расчет текущих транзитов для {user_data.get('username')}")
            
            # Создаем натальный субъект
            natal_subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # Координаты для транзитов
            lat = latitude or user_data.get('latitude', 47.2357)
            lng = longitude or user_data.get('longitude', 39.7015)
            tz = timezone or user_data.get('timezone', "Europe/Moscow")
            
            # Создаем транзитный субъект (текущее время)
            now = datetime.now()
            transit_subject = SubjectFactory.create_subject(
                name="Current Transits",
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=now.minute,
                latitude=lat,
                longitude=lng,
                timezone=tz
            )
            
            # Рассчитываем аспекты между натальной и транзитной картами
            aspects = AspectsCalculator.calculate_dual_chart_aspects(
                natal_subject,
                transit_subject
            )
            
            # Фильтруем аспекты
            filtered_aspects = cls._filter_aspects(
                aspects,
                min_significance=min_significance,
                include_aspects=include_aspects
            )
            
            # Сортируем по значимости
            sorted_aspects = cls._sort_aspects_by_significance(filtered_aspects)
            
            # Формируем результат
            result = cls._format_transit_result(
                transit_date=now.isoformat(),
                natal_subject=natal_subject,
                transit_subject=transit_subject,
                aspects=sorted_aspects,
                all_aspects=aspects,
                location={"latitude": lat, "longitude": lng, "timezone": tz}
            )
            
            logger.info(f"Транзиты рассчитаны. Найдено: {len(aspects)} аспектов, отфильтровано: {len(sorted_aspects)}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета транзитов: {e}")
            raise TransitCalculationError(f"Не удалось рассчитать транзиты: {e}")
    
    @classmethod
    def calculate_transits_for_date(
        cls,
        user_data: Dict[str, Any],
        target_date: Union[str, datetime],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        min_significance: int = 2,
        include_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает транзиты на указанную дату.
        
        Args:
            user_data: Данные пользователя
            target_date: Дата в формате "YYYY-MM-DD" или datetime
            latitude: Широта для транзитов
            longitude: Долгота для транзитов
            timezone: Часовой пояс
            min_significance: Минимальная значимость аспекта
            include_aspects: Список аспектов для включения
            
        Returns:
            Dict: Данные о транзитах
        """
        try:
            # Преобразуем дату
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, "%Y-%m-%d")
            
            logger.info(f"Расчет транзитов на {target_date.strftime('%Y-%m-%d')} для {user_data.get('username')}")
            
            # Создаем натальный субъект
            natal_subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # Координаты для транзитов
            lat = latitude or user_data.get('latitude', 47.2357)
            lng = longitude or user_data.get('longitude', 39.7015)
            tz = timezone or user_data.get('timezone', "Europe/Moscow")
            
            # Создаем транзитный субъект на указанную дату (полдень)
            transit_subject = SubjectFactory.create_subject(
                name=f"Transits for {target_date.strftime('%Y-%m-%d')}",
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
                hour=12,
                minute=0,
                latitude=lat,
                longitude=lng,
                timezone=tz
            )
            
            # Рассчитываем аспекты
            aspects = AspectsCalculator.calculate_dual_chart_aspects(
                natal_subject,
                transit_subject
            )
            
            # Фильтруем
            filtered_aspects = cls._filter_aspects(
                aspects,
                min_significance=min_significance,
                include_aspects=include_aspects
            )
            
            sorted_aspects = cls._sort_aspects_by_significance(filtered_aspects)
            
            # Формируем результат в том же формате, что и calculate_current_transits
            result = cls._format_transit_result(
                transit_date=target_date.isoformat(),
                natal_subject=natal_subject,
                transit_subject=transit_subject,
                aspects=sorted_aspects,
                all_aspects=aspects,
                location={"latitude": lat, "longitude": lng, "timezone": tz}
            )
            
            logger.info(f"Транзиты на {target_date.strftime('%Y-%m-%d')} рассчитаны. Найдено: {len(aspects)} аспектов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета транзитов на дату: {e}")
            raise TransitCalculationError(f"Не удалось рассчитать транзиты на указанную дату: {e}")
    
    @classmethod
    def calculate_transits_period(
        cls,
        user_data: Dict[str, Any],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        step_days: int = 1,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        min_significance: int = 2,
        include_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает транзиты за период.
        Использует ручной расчет аспектов для каждого дня.
        """
        try:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            logger.info(f"Расчет транзитов за период {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
            
            natal_subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            lat = latitude or user_data.get('latitude', 47.2357)
            lng = longitude or user_data.get('longitude', 39.7015)
            tz = timezone or user_data.get('timezone', "Europe/Moscow")
            
            daily_transits = []
            current_date = start_date
            
            while current_date <= end_date:
                # Создаем транзитный субъект на текущую дату (полдень)
                transit_subject = SubjectFactory.create_subject(
                    name=f"Transits for {current_date.strftime('%Y-%m-%d')}",
                    year=current_date.year,
                    month=current_date.month,
                    day=current_date.day,
                    hour=12,
                    minute=0,
                    latitude=lat,
                    longitude=lng,
                    timezone=tz
                )
                
                # Ручной расчет аспектов
                aspects = AspectsCalculator.calculate_dual_chart_aspects(
                    natal_subject,
                    transit_subject
                )
                
                filtered = cls._filter_aspects(
                    aspects,
                    min_significance=min_significance,
                    include_aspects=include_aspects
                )
                
                sorted_aspects = cls._sort_aspects_by_significance(filtered)
                
                daily_transits.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "aspects_count": len(sorted_aspects),
                    "total_aspects": len(aspects),
                    "aspects": sorted_aspects,
                    "all_aspects": aspects
                })
                
                current_date += timedelta(days=step_days)
            
            # Самые значимые дни
            significant_days = sorted(
                daily_transits,
                key=lambda x: x['aspects_count'],
                reverse=True
            )[:5]
            
            result = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "step_days": step_days,
                    "total_days": len(daily_transits)
                },
                "location": {
                    "latitude": lat,
                    "longitude": lng,
                    "timezone": tz
                },
                "daily_transits": daily_transits,
                "significant_days": significant_days,
                "statistics": cls._calculate_period_statistics(daily_transits)
            }
            
            logger.info(f"Транзиты за период рассчитаны. Обработано дней: {len(daily_transits)}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета транзитов за период: {e}")
            raise TransitCalculationError(f"Не удалось рассчитать транзиты за период: {e}")
    
    @classmethod
    def _filter_aspects(
        cls,
        aspects: List[Dict[str, Any]],
        min_significance: int = 2,
        include_aspects: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Фильтрует аспекты по значимости и типу.
        """
        filtered = []
        
        for aspect in aspects:
            aspect_name = aspect.get('aspect', 'Unknown')
            
            # Проверка по типу аспекта
            if include_aspects and aspect_name not in include_aspects:
                continue
            
            # Проверка по значимости
            significance = cls.ASPECT_SIGNIFICANCE.get(aspect_name, 0)
            if significance >= min_significance:
                filtered.append(aspect)
        
        return filtered
    
    @classmethod
    def _sort_aspects_by_significance(
        cls,
        aspects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Сортирует аспекты по значимости и орбису.
        """
        def sort_key(aspect):
            aspect_name = aspect.get('aspect', 'Unknown')
            significance = cls.ASPECT_SIGNIFICANCE.get(aspect_name, 0)
            orbit = aspect.get('orbit', 10)
            # Чем меньше орбис, тем важнее
            return (-significance, orbit)
        
        return sorted(aspects, key=sort_key)
    
    @classmethod
    def _format_transit_result(
        cls,
        transit_date: str,
        natal_subject,
        transit_subject,
        aspects: List[Dict[str, Any]],
        all_aspects: List[Dict[str, Any]],
        location: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Форматирует результат транзитов в структурированный словарь.
        """
        # Получаем позиции транзитных планет
        transit_positions = {}
        for planet_name in cls.TRANSIT_PLANETS:
            planet = getattr(transit_subject, planet_name.lower(), None)
            if planet is not None:
                sign = getattr(planet, 'sign', 'Unknown')
                if hasattr(sign, 'sign'):
                    sign = sign.sign
                transit_positions[planet_name] = {
                    "sign": str(sign),
                    "degree": round(getattr(planet, 'position', 0), 2),
                    "abs_pos": round(getattr(planet, 'abs_pos', 0), 2),
                    "retrograde": getattr(planet, 'retrograde', False)
                }
        
        # Группируем аспекты по планете
        aspects_by_planet = {}
        for aspect in aspects:
            p1 = aspect.get('planet1', '')
            if p1 not in aspects_by_planet:
                aspects_by_planet[p1] = []
            aspects_by_planet[p1].append(aspect)
        
        # Вычисляем общую оценку дня
        day_score = cls._calculate_day_score(aspects)
        
        return {
            "transit_date": transit_date,
            "location": location,
            "natal_subject_name": natal_subject.name,
            "transit_positions": transit_positions,
            "aspects": {
                "total": len(aspects),
                "total_all": len(all_aspects),
                "list": aspects,
                "by_planet": aspects_by_planet
            },
            "day_score": day_score,
            "summary": cls._generate_summary(aspects, day_score)
        }
    
    @classmethod
    def _calculate_day_score(cls, aspects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Вычисляет общую оценку дня на основе аспектов.
        """
        scores = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for aspect in aspects:
            aspect_name = aspect.get('aspect', '')
            significance = cls.ASPECT_SIGNIFICANCE.get(aspect_name, 0)
            
            if aspect_name in ['Trine', 'Sextile']:
                scores['positive'] += significance
            elif aspect_name in ['Square', 'Opposition']:
                scores['negative'] += significance
            else:
                scores['neutral'] += significance
        
        total = scores['positive'] + scores['negative'] + scores['neutral']
        
        # Общая оценка от -10 до +10
        overall = 0
        if total > 0:
            overall = round((scores['positive'] - scores['negative']) / total * 10, 1)
        
        return {
            "overall": overall,
            "positive": scores['positive'],
            "negative": scores['negative'],
            "neutral": scores['neutral'],
            "level": cls._get_day_level(overall)
        }
    
    @classmethod
    def _get_day_level(cls, score: float) -> str:
        """
        Определяет уровень дня на основе оценки.
        """
        if score >= 5:
            return "excellent"
        elif score >= 3:
            return "good"
        elif score >= -3:
            return "neutral"
        elif score >= -5:
            return "challenging"
        else:
            return "difficult"
    
    @classmethod
    def _generate_summary(cls, aspects: List[Dict[str, Any]], day_score: Dict[str, Any]) -> str:
        """
        Генерирует краткое описание дня.
        """
        if not aspects:
            return "Спокойный день без значительных транзитов."
        
        level = day_score.get('level', 'neutral')
        
        if level == 'excellent':
            return "Благоприятный день! Много позитивных аспектов. Хорошее время для начинаний."
        elif level == 'good':
            return "Удачный день. Есть хорошие возможности, но стоит избегать поспешных решений."
        elif level == 'neutral':
            return "Нейтральный день. Нет сильных влияний, можно заниматься текущими делами."
        elif level == 'challenging':
            return "Напряженный день. Возможны конфликты и препятствия. Будьте осторожны."
        else:
            return "Сложный день. Рекомендуется избегать важных решений и больше отдыхать."
    
    @classmethod
    def _calculate_period_statistics(
        cls,
        daily_transits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Рассчитывает статистику по периоду.
        """
        if not daily_transits:
            return {
                "total_days": 0,
                "days_with_aspects": 0,
                "avg_aspects_per_day": 0,
                "best_day": None,
                "worst_day": None
            }
        
        days_with_aspects = sum(1 for d in daily_transits if d['aspects_count'] > 0)
        avg_aspects = sum(d['aspects_count'] for d in daily_transits) / len(daily_transits)
        
        # Лучший и худший дни
        best_day = max(daily_transits, key=lambda x: x['aspects_count']) if daily_transits else None
        worst_day = min(daily_transits, key=lambda x: x['aspects_count']) if daily_transits else None
        
        return {
            "total_days": len(daily_transits),
            "days_with_aspects": days_with_aspects,
            "avg_aspects_per_day": round(avg_aspects, 2),
            "best_day": best_day,
            "worst_day": worst_day
        }
    
    @classmethod
    def save_transits_to_file(
        cls,
        transits_data: Dict[str, Any],
        username: str,
        output_dir: Path,
        filename: Optional[str] = None
    ) -> Path:
        """
        Сохраняет данные транзитов в JSON файл.
        
        Args:
            transits_data: Данные транзитов
            username: Имя пользователя
            output_dir: Папка для сохранения
            filename: Имя файла (опционально)
            
        Returns:
            Path: Путь к сохраненному файлу
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_transits_{date_str}.json"
        elif not filename.endswith('.json'):
            filename += '.json'
        
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(transits_data, f, indent=4, ensure_ascii=False, default=str)
        
        logger.info(f"Транзиты сохранены в: {file_path}")
        return file_path