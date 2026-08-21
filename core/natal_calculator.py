"""
Модуль для расчета натальной карты
"""
import logging
from typing import Dict, Any, Optional, List

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
        active_points: Optional[List[str]] = None,
        include_minor_aspects: bool = False
    ) -> Dict[str, Any]:
        """
        Рассчитывает натальную карту по данным пользователя.
        
        Args:
            user_data: Данные пользователя (из JSON)
            active_points: Список планет для расчета (опционально)
            include_minor_aspects: Включать ли второстепенные аспекты
            
        Returns:
            Dict: Полные данные натальной карты
        """
        try:
            logger.info(f"Расчет натальной карты для {user_data.get('username')}")
            
            # 1. Создаем субъект
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # 2. Извлекаем положения планет
            positions = cls._extract_planet_positions(subject)
            
            # 3. Извлекаем дома
            houses = cls._extract_houses(subject)
            
            # 4. Извлекаем аспекты (используем уже работающий AspectsCalculator)
            aspects = AspectsCalculator.calculate_single_chart_aspects(
                subject, 
                active_points=active_points,
                include_minor=include_minor_aspects
            )
            
            # 5. Извлекаем асцендент и МЦ
            ascendant = cls._extract_ascendant(subject)
            midheaven = cls._extract_midheaven(subject)
            
            # 6. Собираем результат
            result = {
                "chart": {
                    "positions": positions,
                    "houses": houses,
                    "aspects": aspects,
                    "ascendant": ascendant,
                    "midheaven": midheaven
                },
                "elements": cls._calculate_elements(positions),
                "qualities": cls._calculate_qualities(positions)
            }
            
            logger.info(f"Натальная карта рассчитана успешно. Планет: {len(positions)}, Аспектов: {len(aspects)}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета натальной карты: {e}")
            raise ChartCalculationError(f"Не удалось рассчитать натальную карту: {e}")
    
    @classmethod
    def _extract_planet_positions(cls, subject) -> Dict[str, Any]:
        """Извлекает положения планет из субъекта."""
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
                
                # Получаем знак (может быть строкой или объектом)
                sign = getattr(planet, 'sign', 'Unknown')
                if hasattr(sign, 'sign'):
                    sign = sign.sign
                
                # Получаем позицию
                position = getattr(planet, 'position', 0)
                if position == 0 and hasattr(planet, 'abs_pos'):
                    position = planet.abs_pos % 30
                
                positions[display_name] = {
                    "sign": str(sign),
                    "degree": round(float(position), 2),
                    "house": getattr(planet, 'house', 0),
                    "retrograde": getattr(planet, 'retrograde', False),
                    "abs_pos": round(float(getattr(planet, 'abs_pos', 0)), 2)
                }
        
        return positions
    
    @classmethod
    def _extract_houses(cls, subject) -> Dict[str, Any]:
        """Извлекает данные домов."""
        houses = {}
        
        if hasattr(subject, 'houses'):
            for i, house in enumerate(subject.houses, 1):
                sign = getattr(house, 'sign', 'Unknown')
                if hasattr(sign, 'sign'):
                    sign = sign.sign
                
                houses[str(i)] = {
                    "sign": str(sign),
                    "degree": round(float(getattr(house, 'position', 0)), 2)
                }
        
        return houses
    
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
    def _calculate_elements(cls, positions: Dict[str, Any]) -> Dict[str, float]:
        """Рассчитывает распределение стихий."""
        element_map = {
            'Aries': 'fire', 'Leo': 'fire', 'Sagittarius': 'fire',
            'Taurus': 'earth', 'Virgo': 'earth', 'Capricorn': 'earth',
            'Gemini': 'air', 'Libra': 'air', 'Aquarius': 'air',
            'Cancer': 'water', 'Scorpio': 'water', 'Pisces': 'water'
        }
        
        element_counts = {'fire': 0, 'earth': 0, 'air': 0, 'water': 0}
        total = 0
        
        for planet_data in positions.values():
            sign = planet_data.get('sign', '')
            if sign in element_map:
                element_counts[element_map[sign]] += 1
                total += 1
        
        if total == 0:
            return {'fire': 0, 'earth': 0, 'air': 0, 'water': 0}
        
        return {
            'fire': round(element_counts['fire'] / total * 100, 1),
            'earth': round(element_counts['earth'] / total * 100, 1),
            'air': round(element_counts['air'] / total * 100, 1),
            'water': round(element_counts['water'] / total * 100, 1)
        }
    
    @classmethod
    def _calculate_qualities(cls, positions: Dict[str, Any]) -> Dict[str, float]:
        """Рассчитывает распределение качеств."""
        quality_map = {
            'Aries': 'cardinal', 'Cancer': 'cardinal', 'Libra': 'cardinal', 'Capricorn': 'cardinal',
            'Taurus': 'fixed', 'Leo': 'fixed', 'Scorpio': 'fixed', 'Aquarius': 'fixed',
            'Gemini': 'mutable', 'Virgo': 'mutable', 'Sagittarius': 'mutable', 'Pisces': 'mutable'
        }
        
        quality_counts = {'cardinal': 0, 'fixed': 0, 'mutable': 0}
        total = 0
        
        for planet_data in positions.values():
            sign = planet_data.get('sign', '')
            if sign in quality_map:
                quality_counts[quality_map[sign]] += 1
                total += 1
        
        if total == 0:
            return {'cardinal': 0, 'fixed': 0, 'mutable': 0}
        
        return {
            'cardinal': round(quality_counts['cardinal'] / total * 100, 1),
            'fixed': round(quality_counts['fixed'] / total * 100, 1),
            'mutable': round(quality_counts['mutable'] / total * 100, 1)
        }