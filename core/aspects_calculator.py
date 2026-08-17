"""
Модуль для расчета аспектов
"""
import logging
from typing import List, Dict, Any, Optional

from core.exceptions import AspectCalculationError

logger = logging.getLogger(__name__)


class AspectsCalculator:
    """
    Калькулятор аспектов между планетами.
    """
    
    # Определения аспектов
    ASPECT_DEFINITIONS = [
        (0, 'Conjunction', 8),
        (60, 'Sextile', 6),
        (90, 'Square', 8),
        (120, 'Trine', 8),
        (180, 'Opposition', 8),
        (30, 'Semi-sextile', 2),
        (45, 'Semi-square', 2),
        (135, 'Sesquiquadrate', 2),
        (150, 'Quincunx', 2),
    ]
    
    @classmethod
    def calculate_single_chart_aspects(
        cls,
        subject,
        active_points: Optional[List[str]] = None,
        include_minor: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Рассчитывает аспекты внутри одной карты.
        
        Args:
            subject: AstrologicalSubject
            active_points: Список планет для расчета
            include_minor: Включать ли второстепенные аспекты
            
        Returns:
            List[Dict]: Список аспектов
        """
        try:
            # Пробуем использовать встроенный метод Kerykeion
            try:
                from kerykeion import AspectsFactory
                
                if active_points:
                    aspects_data = AspectsFactory.single_chart_aspects(
                        subject,
                        active_points=active_points
                    )
                else:
                    aspects_data = AspectsFactory.single_chart_aspects(subject)
                
                aspects = []
                for aspect in aspects_data.aspects:
                    aspects.append({
                        "planet1": aspect.p1_name,
                        "planet2": aspect.p2_name,
                        "aspect": aspect.aspect,
                        "orbit": round(aspect.orbit, 2),
                        "angle": round(aspect.angle, 2),
                        "movement": getattr(aspect, 'aspect_movement', 'Unknown')
                    })
                
                if aspects:
                    logger.info(f"Найдено {len(aspects)} аспектов через AspectsFactory")
                    return aspects
                    
            except (ImportError, AttributeError, Exception) as e:
                logger.info(f"AspectsFactory не сработал: {e}, переходим к ручному расчету")
            
            # Ручной расчет аспектов
            return cls._calculate_aspects_manual(subject, active_points, include_minor)
            
        except Exception as e:
            logger.error(f"Ошибка расчета аспектов: {e}")
            raise AspectCalculationError(f"Не удалось рассчитать аспекты: {e}")
    
    @classmethod
    def _calculate_aspects_manual(
        cls,
        subject,
        active_points: Optional[List[str]] = None,
        include_minor: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Ручной расчет аспектов (обход проблем с AspectsFactory).
        """
        aspects_list = []
        
        # Список планет
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto"
        ]
        
        if include_minor:
            planet_names.extend(["chiron", "lilith", "true_north_lunar_node"])
        
        # Фильтруем по active_points
        if active_points:
            planet_names = [p for p in planet_names if p.capitalize() in active_points]
        
        # Собираем позиции планет
        planets = []
        for name in planet_names:
            planet = getattr(subject, name, None)
            if planet is not None:
                abs_pos = getattr(planet, 'abs_pos', None)
                if abs_pos is None:
                    sign_num = getattr(planet, 'sign_num', 0)
                    position = getattr(planet, 'position', 0)
                    abs_pos = sign_num * 30 + position
                
                planets.append({
                    'name': name.capitalize(),
                    'abs_pos': abs_pos,
                    'sign': getattr(planet, 'sign', 'Unknown')
                })
        
        # Выбираем определения аспектов
        aspect_defs = cls.ASPECT_DEFINITIONS.copy()
        if not include_minor:
            aspect_defs = [a for a in aspect_defs if a[1] in ['Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition']]
        
        # Перебираем все пары планет
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                
                # Вычисляем угол
                angle = abs(p1['abs_pos'] - p2['abs_pos'])
                if angle > 180:
                    angle = 360 - angle
                
                # Проверяем каждый тип аспекта
                for target_angle, aspect_name, orb in aspect_defs:
                    diff = abs(angle - target_angle)
                    if diff <= orb:
                        aspects_list.append({
                            'planet1': p1['name'],
                            'planet2': p2['name'],
                            'aspect': aspect_name,
                            'orbit': round(diff, 2),
                            'angle': round(angle, 2),
                            'movement': 'Unknown'
                        })
                        break
        
        logger.info(f"Ручной расчет: найдено {len(aspects_list)} аспектов")
        return aspects_list
    
    @classmethod
    def calculate_dual_chart_aspects(
        cls,
        subject1,
        subject2,
        active_points: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Рассчитывает аспекты между двумя картами (синастрия, транзиты).
        
        Args:
            subject1: Первый астрологический субъект
            subject2: Второй астрологический субъект
            active_points: Список планет для расчета
            
        Returns:
            List[Dict]: Список аспектов
        """
        try:
            from kerykeion import AspectsFactory
            
            if active_points:
                aspects_data = AspectsFactory.dual_chart_aspects(
                    subject1,
                    subject2,
                    active_points=active_points
                )
            else:
                aspects_data = AspectsFactory.dual_chart_aspects(subject1, subject2)
            
            aspects = []
            for aspect in aspects_data.aspects:
                aspects.append({
                    "planet1": aspect.p1_name,
                    "planet2": aspect.p2_name,
                    "aspect": aspect.aspect,
                    "orbit": round(aspect.orbit, 2),
                    "angle": round(aspect.angle, 2),
                    "movement": getattr(aspect, 'aspect_movement', 'Unknown')
                })
            
            logger.info(f"Найдено {len(aspects)} межкарточных аспектов")
            return aspects
            
        except Exception as e:
            logger.error(f"Ошибка расчета межкарточных аспектов: {e}")
            raise AspectCalculationError(f"Не удалось рассчитать аспекты между картами: {e}")