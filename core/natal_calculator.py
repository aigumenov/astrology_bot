"""
Модуль для расчета натальной карты
"""
import logging
from typing import Dict, Any, Optional, List

from kerykeion import ChartDataFactory

from core.subject_factory import SubjectFactory
from core.aspects_calculator import AspectsCalculator
from core.exceptions import ChartCalculationError

logger = logging.getLogger(__name__)


class NatalCalculator:
    """
    Калькулятор натальной карты.
    Рассчитывает полные данные натальной карты.
    """
    
    @classmethod
    def calculate(
        cls,
        user_data: Dict[str, Any],
        active_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Рассчитывает натальную карту по данным пользователя.
        
        Args:
            user_data: Данные пользователя (из JSON)
            active_points: Список планет для расчета (опционально)
            
        Returns:
            Dict: Полные данные натальной карты
        """
        try:
            logger.info(f"Расчет натальной карты для {user_data.get('username')}")
            
            # 1. Создаем субъект
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # 2. Создаем данные карты
            chart_data = ChartDataFactory.create_natal_chart_data(
                subject,
                active_points=active_points
            )
            
            # 3. Извлекаем аспекты
            aspects = AspectsCalculator.calculate_single_chart_aspects(subject)
            
            # 4. Формируем структурированный результат
            result = cls._format_chart_data(subject, chart_data, aspects)
            
            logger.info(f"Натальная карта рассчитана успешно")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета натальной карты: {e}")
            raise ChartCalculationError(f"Не удалось рассчитать натальную карту: {e}")
    
    @classmethod
    def _format_chart_data(
        cls,
        subject,
        chart_data,
        aspects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Форматирует данные карты в структурированный словарь.
        """
        # Извлечение положений планет
        positions = {}
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto",
            "chiron", "lilith", "true_north_lunar_node", "fortune"
        ]
        
        for name in planet_names:
            planet = getattr(subject, name, None)
            if planet is not None:
                display_name = name.replace('_', ' ').title()
                if name == "true_north_lunar_node":
                    display_name = "North Node"
                elif name == "lilith":
                    display_name = "Lilith"
                
                positions[display_name] = {
                    "sign": planet.sign,
                    "degree": round(getattr(planet, 'position', 0), 2),
                    "house": getattr(planet, 'house', 0),
                    "retrograde": getattr(planet, 'retrograde', False),
                    "abs_pos": round(getattr(planet, 'abs_pos', 0), 2)
                }
        
        # Извлечение домов
        houses = {}
        if hasattr(subject, 'houses'):
            for i, house in enumerate(subject.houses, 1):
                houses[str(i)] = {
                    "sign": house.sign,
                    "degree": round(getattr(house, 'position', 0), 2)
                }
        
        # Извлечение асцендента и МЦ
        asc_sign = getattr(subject, 'ascendant', 'Unknown')
        if hasattr(asc_sign, 'sign'):
            asc_sign = asc_sign.sign
        
        asc_degree = getattr(subject, 'ascendant_degree', 0)
        if asc_degree == 0 and hasattr(subject, 'ascendant') and hasattr(subject.ascendant, 'position'):
            asc_degree = subject.ascendant.position
        
        mc_sign = getattr(subject, 'midheaven', 'Unknown')
        if hasattr(mc_sign, 'sign'):
            mc_sign = mc_sign.sign
        
        mc_degree = getattr(subject, 'midheaven_degree', 0)
        if mc_degree == 0 and hasattr(subject, 'midheaven') and hasattr(subject.midheaven, 'position'):
            mc_degree = subject.midheaven.position
        
        return {
            "chart": {
                "positions": positions,
                "houses": houses,
                "aspects": aspects,
                "ascendant": {
                    "sign": str(asc_sign),
                    "degree": round(float(asc_degree), 2)
                },
                "midheaven": {
                    "sign": str(mc_sign),
                    "degree": round(float(mc_degree), 2)
                }
            },
            "elements": {
                "fire": getattr(chart_data.element_distribution, 'fire_percentage', 0),
                "earth": getattr(chart_data.element_distribution, 'earth_percentage', 0),
                "air": getattr(chart_data.element_distribution, 'air_percentage', 0),
                "water": getattr(chart_data.element_distribution, 'water_percentage', 0)
            },
            "qualities": {
                "cardinal": getattr(chart_data.quality_distribution, 'cardinal_percentage', 0),
                "fixed": getattr(chart_data.quality_distribution, 'fixed_percentage', 0),
                "mutable": getattr(chart_data.quality_distribution, 'mutable_percentage', 0)
            }
        }