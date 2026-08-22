"""
Модуль для расчета Солярных и Лунных возвращений

Солярное возвращение (Solar Return) — момент, когда Солнце возвращается 
в натальную позицию. Происходит раз в год (в день рождения).

Лунное возвращение (Lunar Return) — момент, когда Луна возвращается 
в натальную позицию. Происходит примерно раз в месяц (каждые 27-29 дней).

Возвращения используются для прогнозов:
- Солярное: годовой прогноз
- Лунное: месячный прогноз
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

from kerykeion import PlanetaryReturnFactory

from core.subject_factory import SubjectFactory
from core.aspects_calculator import AspectsCalculator
from core.exceptions import TransitCalculationError

logger = logging.getLogger(__name__)


class ReturnsCalculator:
    """
    Калькулятор Солярных и Лунных возвращений.
    """
    
    @classmethod
    def calculate_solar_return(
        cls,
        user_data: Dict[str, Any],
        year: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает Солярное возвращение на указанный год.
        """
        try:
            logger.info(f"Расчет солярного возвращения на {year} год для {user_data.get('username')}")
            
            # Создаем натальный субъект
            natal_subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # Координаты для возвращения
            lat = latitude or user_data.get('latitude', 47.2357)
            lng = longitude or user_data.get('longitude', 39.7015)
            tz = timezone or user_data.get('timezone', "Europe/Moscow")
            city_name = city or user_data.get('place', 'Current Location')
            
            # Создаем фабрику возвращений
            return_factory = PlanetaryReturnFactory(
                subject=natal_subject,
                lat=lat,
                lng=lng,
                tz_str=tz,
                online=False
            )
            
            # Ищем солярное возвращение
            solar_return = return_factory.next_return_from_date(
                year=year,
                month=1,
                day=1,
                return_type="Solar"
            )
            
            # Извлекаем позиции планет из возвращения
            return_positions = cls._extract_positions(solar_return)
            
            # Извлекаем асцендент и МЦ
            ascendant = cls._extract_ascendant(solar_return)
            midheaven = cls._extract_midheaven(solar_return)
            
            # Рассчитываем аспекты в карте возвращения
            aspects = AspectsCalculator.calculate_single_chart_aspects(
                solar_return,
                include_minor=False
            )
            
            # Формируем результат
            result = {
                "type": "Solar",
                "type_name": "Солярное возвращение",
                "return_year": year,
                "return_date": solar_return.iso_formatted_local_datetime,
                "location": {
                    "latitude": lat,
                    "longitude": lng,
                    "timezone": tz,
                    "city": city_name
                },
                "natal_subject_name": natal_subject.name,
                "return_positions": return_positions,
                "ascendant": ascendant,
                "midheaven": midheaven,
                "aspects": {
                    "total": len(aspects),
                    "list": aspects
                },
                "summary": cls._generate_return_summary("Solar", aspects)
            }
            
            logger.info(f"Солярное возвращение на {year} год рассчитано успешно")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета солярного возвращения: {e}")
            raise TransitCalculationError(f"Не удалось рассчитать солярное возвращение: {e}")
    
    @classmethod
    def calculate_lunar_return(
        cls,
        user_data: Dict[str, Any],
        year: int,
        month: int,
        day: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает Лунное возвращение после указанной даты.
        """
        try:
            logger.info(f"Расчет лунного возвращения после {day}-{month}-{year} для {user_data.get('username')}")
            
            # Создаем натальный субъект
            natal_subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # Координаты для возвращения
            lat = latitude or user_data.get('latitude', 47.2357)
            lng = longitude or user_data.get('longitude', 39.7015)
            tz = timezone or user_data.get('timezone', "Europe/Moscow")
            city_name = city or user_data.get('place', 'Current Location')
            
            # Создаем фабрику возвращений
            return_factory = PlanetaryReturnFactory(
                subject=natal_subject,
                lat=lat,
                lng=lng,
                tz_str=tz,
                online=False
            )
            
            # Ищем лунное возвращение
            lunar_return = return_factory.next_return_from_date(
                year=year,
                month=month,
                day=day,
                return_type="Lunar"
            )
            
            # Извлекаем позиции планет из возвращения
            return_positions = cls._extract_positions(lunar_return)
            
            # Извлекаем асцендент и МЦ
            ascendant = cls._extract_ascendant(lunar_return)
            midheaven = cls._extract_midheaven(lunar_return)
            
            # Рассчитываем аспекты в карте возвращения
            aspects = AspectsCalculator.calculate_single_chart_aspects(
                lunar_return,
                include_minor=False
            )
            
            # Формируем результат
            result = {
                "type": "Lunar",
                "type_name": "Лунное возвращение",
                "return_year": year,
                "return_date": lunar_return.iso_formatted_local_datetime,
                "location": {
                    "latitude": lat,
                    "longitude": lng,
                    "timezone": tz,
                    "city": city_name
                },
                "natal_subject_name": natal_subject.name,
                "return_positions": return_positions,
                "ascendant": ascendant,
                "midheaven": midheaven,
                "aspects": {
                    "total": len(aspects),
                    "list": aspects
                },
                "summary": cls._generate_return_summary("Lunar", aspects)
            }
            
            logger.info(f"Лунное возвращение после {day}-{month}-{year} рассчитано успешно")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета лунного возвращения: {e}")
            raise TransitCalculationError(f"Не удалось рассчитать лунное возвращение: {e}")
    
    @classmethod
    def calculate_next_lunar_return(
        cls,
        user_data: Dict[str, Any],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        """Рассчитывает следующее Лунное возвращение от текущей даты."""
        now = datetime.now()
        return cls.calculate_lunar_return(
            user_data=user_data,
            year=now.year,
            month=now.month,
            day=now.day,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            city=city
        )
    
    @classmethod
    def calculate_multiple_lunar_returns(
        cls,
        user_data: Dict[str, Any],
        count: int = 3,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: str = "Europe/Moscow",
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает несколько следующих Лунных возвращений.
        """
        try:
            logger.info(f"Расчет {count} следующих лунных возвращений для {user_data.get('username')}")
            
            results = []
            current_date = datetime.now()
            
            for i in range(count):
                lunar_data = cls.calculate_lunar_return(
                    user_data=user_data,
                    year=current_date.year,
                    month=current_date.month,
                    day=current_date.day,
                    latitude=latitude,
                    longitude=longitude,
                    timezone=timezone,
                    city=city
                )
                results.append(lunar_data)
                
                # Сдвигаем дату на 2 дня после найденного возвращения
                return_date = datetime.fromisoformat(lunar_data['return_date'])
                current_date = return_date + timedelta(days=2)
            
            return {
                "type": "Lunar_Returns",
                "type_name": "Несколько лунных возвращений",
                "count": count,
                "location": {
                    "latitude": latitude or user_data.get('latitude', 47.2357),
                    "longitude": longitude or user_data.get('longitude', 39.7015),
                    "timezone": timezone or user_data.get('timezone', "Europe/Moscow"),
                    "city": city or user_data.get('place', 'Current Location')
                },
                "returns": results
            }
            
        except Exception as e:
            logger.error(f"Ошибка расчета нескольких лунных возвращений: {e}")
            raise TransitCalculationError(f"Не удалось рассчитать лунные возвращения: {e}")
    
    @classmethod
    def _extract_positions(cls, subject) -> Dict[str, Any]:
        """Извлекает положения планет из субъекта."""
        positions = {}
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto"
        ]
        
        for name in planet_names:
            planet = getattr(subject, name, None)
            if planet is not None:
                sign = getattr(planet, 'sign', 'Unknown')
                if hasattr(sign, 'sign'):
                    sign = sign.sign
                positions[name.capitalize()] = {
                    "sign": str(sign),
                    "degree": round(getattr(planet, 'position', 0), 2),
                    "abs_pos": round(getattr(planet, 'abs_pos', 0), 2),
                    "house": getattr(planet, 'house', 0),
                    "retrograde": getattr(planet, 'retrograde', False)
                }
        return positions
    
    @classmethod
    def _extract_ascendant(cls, subject) -> Dict[str, Any]:
        """Извлекает асцендент."""
        asc_sign = None
        asc_degree = 0
        
        if hasattr(subject, 'ascendant'):
            asc = subject.ascendant
            if hasattr(asc, 'sign'):
                asc_sign = asc.sign
                asc_degree = getattr(asc, 'position', 0)
            else:
                asc_sign = str(asc)
        
        if asc_sign is None and hasattr(subject, 'asc'):
            asc_sign = subject.asc
        
        if asc_sign is None and hasattr(subject, 'ascendant_object'):
            asc_obj = subject.ascendant_object
            asc_sign = asc_obj.sign
            asc_degree = asc_obj.position
        
        return {
            "sign": str(asc_sign) if asc_sign else "Unknown",
            "degree": round(float(asc_degree or 0), 2)
        }
    
    @classmethod
    def _extract_midheaven(cls, subject) -> Dict[str, Any]:
        """Извлекает МЦ (Midheaven)."""
        mc_sign = None
        mc_degree = 0
        
        if hasattr(subject, 'midheaven'):
            mc = subject.midheaven
            if hasattr(mc, 'sign'):
                mc_sign = mc.sign
                mc_degree = getattr(mc, 'position', 0)
            else:
                mc_sign = str(mc)
        
        if mc_sign is None and hasattr(subject, 'mc'):
            mc_sign = subject.mc
        
        if mc_sign is None and hasattr(subject, 'midheaven_object'):
            mc_obj = subject.midheaven_object
            mc_sign = mc_obj.sign
            mc_degree = mc_obj.position
        
        return {
            "sign": str(mc_sign) if mc_sign else "Unknown",
            "degree": round(float(mc_degree or 0), 2)
        }
    
    @classmethod
    def _generate_return_summary(
        cls,
        return_type: str,
        aspects: List[Dict[str, Any]]
    ) -> str:
        """Генерирует краткое описание возвращения."""
        if not aspects:
            if return_type == "Solar":
                return "Спокойный год без значительных аспектов."
            else:
                return "Спокойный месяц без значительных аспектов."
        
        # Считаем позитивные и негативные аспекты
        positive = 0
        negative = 0
        for aspect in aspects:
            aspect_name = aspect.get('aspect', '')
            if aspect_name in ['Trine', 'Sextile']:
                positive += 1
            elif aspect_name in ['Square', 'Opposition']:
                negative += 1
        
        if return_type == "Solar":
            if positive > negative:
                return "Благоприятный год. Много гармоничных аспектов, ожидайте хороших событий."
            elif negative > positive:
                return "Напряженный год. Возможны испытания, но они дадут ценный опыт."
            else:
                return "Сбалансированный год. Будет и хорошее, и сложное."
        else:
            if positive > negative:
                return "Благоприятный месяц. Хорошее время для начинаний и позитивных изменений."
            elif negative > positive:
                return "Напряженный месяц. Стоит быть осторожным и не принимать поспешных решений."
            else:
                return "Сбалансированный месяц. Можно спокойно заниматься текущими делами."
    
    @classmethod
    def save_return_to_file(
        cls,
        return_data: Dict[str, Any],
        username: str,
        output_dir: Path,
        filename: Optional[str] = None
    ) -> Path:
        """
        Сохраняет данные возвращения в JSON файл.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            return_type = return_data.get('type', 'Return')
            return_year = return_data.get('return_year', '')
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_{return_type.lower()}_return_{return_year}_{date_str}.json"
        elif not filename.endswith('.json'):
            filename += '.json'
        
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(return_data, f, indent=4, ensure_ascii=False, default=str)
        
        logger.info(f"Возвращение сохранено в: {file_path}")
        return file_path