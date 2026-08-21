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
    
    # Маппинг знаков к стихиям (на русском и английском)
    ELEMENT_MAP = {
        'Овен': 'fire', 'Лев': 'fire', 'Стрелец': 'fire',
        'Телец': 'earth', 'Дева': 'earth', 'Козерог': 'earth',
        'Близнецы': 'air', 'Весы': 'air', 'Водолей': 'air',
        'Рак': 'water', 'Скорпион': 'water', 'Рыбы': 'water',
        # Английские названия
        'Aries': 'fire', 'Leo': 'fire', 'Sagittarius': 'fire',
        'Taurus': 'earth', 'Virgo': 'earth', 'Capricorn': 'earth',
        'Gemini': 'air', 'Libra': 'air', 'Aquarius': 'air',
        'Cancer': 'water', 'Scorpio': 'water', 'Pisces': 'water',
        # Сокращения
        'Sag': 'fire', 'Vir': 'earth', 'Sco': 'water', 'Aqu': 'air',
        'Cap': 'earth', 'Lib': 'air', 'Can': 'water', 'Leo': 'fire',
        'Gem': 'air', 'Tau': 'earth', 'Ari': 'fire', 'Pis': 'water'
    }
    
    # Маппинг знаков к качествам
    QUALITY_MAP = {
        'Овен': 'cardinal', 'Рак': 'cardinal', 'Весы': 'cardinal', 'Козерог': 'cardinal',
        'Телец': 'fixed', 'Лев': 'fixed', 'Скорпион': 'fixed', 'Водолей': 'fixed',
        'Близнецы': 'mutable', 'Дева': 'mutable', 'Стрелец': 'mutable', 'Рыбы': 'mutable',
        # Английские названия
        'Aries': 'cardinal', 'Cancer': 'cardinal', 'Libra': 'cardinal', 'Capricorn': 'cardinal',
        'Taurus': 'fixed', 'Leo': 'fixed', 'Scorpio': 'fixed', 'Aquarius': 'fixed',
        'Gemini': 'mutable', 'Virgo': 'mutable', 'Sagittarius': 'mutable', 'Pisces': 'mutable',
        # Сокращения
        'Sag': 'mutable', 'Vir': 'mutable', 'Sco': 'fixed', 'Aqu': 'fixed',
        'Cap': 'cardinal', 'Lib': 'cardinal', 'Can': 'cardinal', 'Leo': 'fixed',
        'Gem': 'mutable', 'Tau': 'fixed', 'Ari': 'cardinal', 'Pis': 'mutable'
    }
    
    @classmethod
    def calculate(
        cls,
        user_data: Dict[str, Any],
        active_points: Optional[List[str]] = None,
        include_minor_aspects: bool = False
    ) -> Dict[str, Any]:
        """
        Рассчитывает натальную карту по данным пользователя.
        """
        try:
            logger.info(f"Расчет натальной карты для {user_data.get('username')}")
            
            # 1. Создаем субъект
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # 2. Извлекаем положения планет
            positions = cls._extract_planet_positions(subject)
            
            # 3. Извлекаем дома
            houses = cls._extract_houses(subject)
            
            # 4. Извлекаем аспекты
            aspects = AspectsCalculator.calculate_single_chart_aspects(
                subject, 
                active_points=active_points,
                include_minor=include_minor_aspects
            )
            
            # 5. Извлекаем асцендент и МЦ
            ascendant = cls._extract_ascendant(subject)
            midheaven = cls._extract_midheaven(subject)
            
            # 6. Рассчитываем элементы и качества из positions
            elements = cls._calculate_elements_from_positions(positions)
            qualities = cls._calculate_qualities_from_positions(positions)
            
            # 7. Собираем результат
            result = {
                "chart": {
                    "positions": positions,
                    "houses": houses,
                    "aspects": aspects,
                    "ascendant": ascendant,
                    "midheaven": midheaven
                },
                "elements": elements,
                "qualities": qualities
            }
            
            logger.info(f"Натальная карта рассчитана. Планет: {len(positions)}, Домов: {len(houses)}, Аспектов: {len(aspects)}")
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
                elif name == "sun":
                    display_name = "Sun"
                elif name == "moon":
                    display_name = "Moon"
                elif name == "mercury":
                    display_name = "Mercury"
                elif name == "venus":
                    display_name = "Venus"
                elif name == "mars":
                    display_name = "Mars"
                elif name == "jupiter":
                    display_name = "Jupiter"
                elif name == "saturn":
                    display_name = "Saturn"
                elif name == "uranus":
                    display_name = "Uranus"
                elif name == "neptune":
                    display_name = "Neptune"
                elif name == "pluto":
                    display_name = "Pluto"
                
                # Получаем знак
                sign = getattr(planet, 'sign', 'Unknown')
                if hasattr(sign, 'sign'):
                    sign = sign.sign
                elif hasattr(sign, '__str__'):
                    sign = str(sign)
                
                # Получаем позицию
                position = getattr(planet, 'position', 0)
                if position == 0 and hasattr(planet, 'abs_pos'):
                    position = planet.abs_pos % 30
                
                # Получаем дом
                house = getattr(planet, 'house', 0)
                if hasattr(house, 'house'):
                    house = house.house
                
                positions[display_name] = {
                    "sign": str(sign),
                    "degree": round(float(position), 2),
                    "house": house,
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
                elif hasattr(sign, '__str__'):
                    sign = str(sign)
                
                degree = getattr(house, 'position', 0)
                if degree == 0 and hasattr(house, 'abs_pos'):
                    degree = house.abs_pos % 30
                
                houses[str(i)] = {
                    "sign": str(sign),
                    "degree": round(float(degree), 2)
                }
        
        # Если дома не найдены, создаем на основе Асцендента
        if not houses:
            logger.warning("Дома не найдены, создаем на основе Асцендента")
            asc_sign = None
            if hasattr(subject, 'ascendant'):
                asc = subject.ascendant
                if hasattr(asc, 'sign'):
                    asc_sign = asc.sign
                elif hasattr(asc, 'sign_num'):
                    asc_sign = asc.sign_num
                elif hasattr(asc, '__str__'):
                    asc_sign = str(asc)
            
            if asc_sign:
                sign_order = [
                    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
                ]
                try:
                    start_idx = sign_order.index(asc_sign)
                except (ValueError, AttributeError):
                    start_idx = 0
                
                for i in range(12):
                    sign_idx = (start_idx + i) % 12
                    houses[str(i + 1)] = {
                        "sign": sign_order[sign_idx],
                        "degree": 0.0
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
    def _calculate_elements_from_positions(cls, positions: Dict[str, Any]) -> Dict[str, float]:
        """
        Рассчитывает распределение стихий на основе positions.
        """
        element_counts = {'fire': 0, 'earth': 0, 'air': 0, 'water': 0}
        total = 0
        
        for planet_data in positions.values():
            sign = planet_data.get('sign', '')
            if sign and sign in cls.ELEMENT_MAP:
                element = cls.ELEMENT_MAP[sign]
                element_counts[element] += 1
                total += 1
            else:
                # Пробуем найти знак в маппинге по частичному совпадению
                for key, value in cls.ELEMENT_MAP.items():
                    if key.lower() in sign.lower() or sign.lower() in key.lower():
                        element_counts[value] += 1
                        total += 1
                        break
        
        if total == 0:
            # Если ничего не найдено, используем равномерное распределение
            logger.warning("Не найдено планет для расчета элементов. Используем равномерное распределение.")
            return {'fire': 25.0, 'earth': 25.0, 'air': 25.0, 'water': 25.0}
        
        return {
            'fire': round(element_counts['fire'] / total * 100, 1),
            'earth': round(element_counts['earth'] / total * 100, 1),
            'air': round(element_counts['air'] / total * 100, 1),
            'water': round(element_counts['water'] / total * 100, 1)
        }
    
    @classmethod
    def _calculate_qualities_from_positions(cls, positions: Dict[str, Any]) -> Dict[str, float]:
        """
        Рассчитывает распределение качеств на основе positions.
        """
        quality_counts = {'cardinal': 0, 'fixed': 0, 'mutable': 0}
        total = 0
        
        for planet_data in positions.values():
            sign = planet_data.get('sign', '')
            if sign and sign in cls.QUALITY_MAP:
                quality = cls.QUALITY_MAP[sign]
                quality_counts[quality] += 1
                total += 1
            else:
                # Пробуем найти знак в маппинге по частичному совпадению
                for key, value in cls.QUALITY_MAP.items():
                    if key.lower() in sign.lower() or sign.lower() in key.lower():
                        quality_counts[value] += 1
                        total += 1
                        break
        
        if total == 0:
            # Если ничего не найдено, используем равномерное распределение
            logger.warning("Не найдено планет для расчета качеств. Используем равномерное распределение.")
            return {'cardinal': 33.3, 'fixed': 33.3, 'mutable': 33.3}
        
        return {
            'cardinal': round(quality_counts['cardinal'] / total * 100, 1),
            'fixed': round(quality_counts['fixed'] / total * 100, 1),
            'mutable': round(quality_counts['mutable'] / total * 100, 1)
        }