"""
Модуль для расчета Синастрии (совместимости)

Синастрия — это раздел астрологии, который сравнивает две натальные карты
для анализа совместимости и динамики отношений.

Модуль позволяет:
1. Сравнивать две натальные карты
2. Рассчитывать аспекты между планетами двух людей
3. Вычислять числовой балл совместимости
4. Анализировать сильные и слабые стороны отношений
5. Генерировать текстовый отчет о совместимости

Возвращает структурированный JSON для использования в других модулях.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

from core.subject_factory import SubjectFactory
from core.aspects_calculator import AspectsCalculator
from core.exceptions import SynastryCalculationError

logger = logging.getLogger(__name__)


class SynastryCalculator:
    """
    Калькулятор синастрии (совместимости).
    """
    
    # Значимость аспектов для оценки совместимости
    ASPECT_WEIGHTS = {
        'Conjunction': 5,
        'Opposition': 4,
        'Square': 3,
        'Trine': 4,
        'Sextile': 3,
        'Quincunx': 1,
        'Semi-sextile': 1,
        'Semi-square': 2,
        'Sesquiquadrate': 2,
    }
    
    # Веса планет для оценки совместимости
    PLANET_WEIGHTS = {
        'Sun': 5,
        'Moon': 5,
        'Venus': 4,
        'Mars': 4,
        'Mercury': 3,
        'Jupiter': 3,
        'Saturn': 2,
        'Uranus': 2,
        'Neptune': 2,
        'Pluto': 2,
        'Ascendant': 4,
        'Midheaven': 3,
    }
    
    @classmethod
    def calculate_synastry(
        cls,
        user1_data: Dict[str, Any],
        user2_data: Dict[str, Any],
        include_minor_aspects: bool = False,
        min_significance: int = 2
    ) -> Dict[str, Any]:
        """
        Рассчитывает синастрию между двумя пользователями.
        
        Args:
            user1_data: Данные первого пользователя
            user2_data: Данные второго пользователя
            include_minor_aspects: Включать ли второстепенные аспекты
            min_significance: Минимальная значимость аспекта
            
        Returns:
            Dict: Данные синастрии
        """
        try:
            logger.info(f"Расчет синастрии между {user1_data.get('username')} и {user2_data.get('username')}")
            
            # Создаем субъекты для обоих пользователей
            subject1 = SubjectFactory.create_subject_from_user_data(user1_data)
            subject2 = SubjectFactory.create_subject_from_user_data(user2_data)
            
            # Рассчитываем аспекты между картами
            aspects = AspectsCalculator.calculate_dual_chart_aspects(
                subject1,
                subject2,
                include_minor=include_minor_aspects
            )
            
            # Фильтруем по значимости
            filtered_aspects = cls._filter_aspects_by_significance(
                aspects,
                min_significance=min_significance
            )
            
            # Рассчитываем балл совместимости
            compatibility_score = cls._calculate_compatibility_score(filtered_aspects)
            
            # Анализируем аспекты по категориям
            analysis = cls._analyze_aspects(filtered_aspects)
            
            # Определяем сильные и слабые стороны
            strengths, weaknesses = cls._find_strengths_and_weaknesses(filtered_aspects)
            
            # Генерируем отчет
            report = cls._generate_report(
                user1_data,
                user2_data,
                filtered_aspects,
                compatibility_score,
                analysis,
                strengths,
                weaknesses
            )
            
            result = {
                "user1": {
                    "name": user1_data.get('first_name', 'User1'),
                    "username": user1_data.get('username', 'user1'),
                    "birth_date": user1_data.get('birth_date', ''),
                    "birth_time": user1_data.get('birth_time', '')
                },
                "user2": {
                    "name": user2_data.get('first_name', 'User2'),
                    "username": user2_data.get('username', 'user2'),
                    "birth_date": user2_data.get('birth_date', ''),
                    "birth_time": user2_data.get('birth_time', '')
                },
                "aspects": {
                    "total": len(aspects),
                    "filtered": len(filtered_aspects),
                    "list": filtered_aspects
                },
                "compatibility_score": compatibility_score,
                "analysis": analysis,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "report": report
            }
            
            logger.info(f"Синастрия рассчитана. Найдено аспектов: {len(aspects)}, отфильтровано: {len(filtered_aspects)}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка расчета синастрии: {e}")
            raise SynastryCalculationError(f"Не удалось рассчитать синастрию: {e}")
    
    @classmethod
    def calculate_synastry_by_username(
        cls,
        username1: str,
        username2: str,
        user_repo,
        include_minor_aspects: bool = False,
        min_significance: int = 2
    ) -> Dict[str, Any]:
        """
        Рассчитывает синастрию по именам пользователей.
        
        Args:
            username1: Имя первого пользователя
            username2: Имя второго пользователя
            user_repo: Репозиторий пользователей
            include_minor_aspects: Включать ли второстепенные аспекты
            min_significance: Минимальная значимость аспекта
            
        Returns:
            Dict: Данные синастрии
        """
        user1_data = user_repo.load_user_data(username1)
        user2_data = user_repo.load_user_data(username2)
        
        if not user1_data:
            raise SynastryCalculationError(f"Пользователь {username1} не найден")
        if not user2_data:
            raise SynastryCalculationError(f"Пользователь {username2} не найден")
        
        return cls.calculate_synastry(
            user1_data,
            user2_data,
            include_minor_aspects,
            min_significance
        )
    
    @classmethod
    def _filter_aspects_by_significance(
        cls,
        aspects: List[Dict[str, Any]],
        min_significance: int
    ) -> List[Dict[str, Any]]:
        """Фильтрует аспекты по значимости."""
        filtered = []
        for aspect in aspects:
            aspect_name = aspect.get('aspect', '')
            significance = cls.ASPECT_WEIGHTS.get(aspect_name, 0)
            if significance >= min_significance:
                aspect['significance'] = significance
                filtered.append(aspect)
        return filtered
    
    @classmethod
    def _calculate_compatibility_score(
        cls,
        aspects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Вычисляет балл совместимости.
        """
        total_score = 0
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        # Веса для разных планетных комбинаций
        planet_combinations = {
            ('Sun', 'Moon'): 2.0,
            ('Sun', 'Venus'): 1.8,
            ('Moon', 'Venus'): 1.8,
            ('Venus', 'Mars'): 2.0,
            ('Moon', 'Mars'): 1.5,
            ('Sun', 'Mars'): 1.5,
            ('Mercury', 'Mercury'): 1.2,
            ('Jupiter', 'Jupiter'): 1.0,
            ('Saturn', 'Saturn'): 1.0,
            ('Venus', 'Venus'): 1.5,
            ('Mars', 'Mars'): 1.2,
        }
        
        # Категории аспектов
        aspect_categories = {
            'Conjunction': 'intense',
            'Opposition': 'challenging',
            'Square': 'challenging',
            'Trine': 'harmonious',
            'Sextile': 'harmonious',
            'Quincunx': 'neutral',
            'Semi-sextile': 'neutral',
            'Semi-square': 'challenging',
            'Sesquiquadrate': 'challenging',
        }
        
        for aspect in aspects:
            p1 = aspect.get('planet1', '')
            p2 = aspect.get('planet2', '')
            aspect_name = aspect.get('aspect', '')
            orbit = aspect.get('orbit', 10)
            
            # Базовый вес аспекта
            weight = cls.ASPECT_WEIGHTS.get(aspect_name, 1)
            
            # Бонус за точность орбиса
            orbit_bonus = max(0, 1.0 - (orbit / 10) * 0.5)
            
            # Бонус за важные комбинации планет
            planet_bonus = 1.0
            if (p1, p2) in planet_combinations:
                planet_bonus = planet_combinations[(p1, p2)]
            elif (p2, p1) in planet_combinations:
                planet_bonus = planet_combinations[(p2, p1)]
            
            # Финальный вес аспекта
            aspect_score = weight * orbit_bonus * planet_bonus
            
            # Определяем категорию
            category = aspect_categories.get(aspect_name, 'neutral')
            
            if category == 'harmonious':
                positive_score += aspect_score
            elif category == 'challenging':
                negative_score += aspect_score
            else:
                neutral_score += aspect_score
            
            total_score += aspect_score
        
        # Общий балл от 0 до 100
        max_possible = 100
        normalized_score = min(100, (positive_score / (positive_score + negative_score + 1)) * 100)
        
        # Определяем уровень совместимости
        if normalized_score >= 80:
            level = "excellent"
            description = "Исключительная совместимость! Отличная пара."
        elif normalized_score >= 65:
            level = "very_good"
            description = "Очень хорошая совместимость. Много общего и гармонии."
        elif normalized_score >= 50:
            level = "good"
            description = "Хорошая совместимость. Есть потенциал для развития."
        elif normalized_score >= 35:
            level = "average"
            description = "Средняя совместимость. Потребуются усилия."
        elif normalized_score >= 20:
            level = "below_average"
            description = "Ниже среднего. Возможны сложности."
        else:
            level = "low"
            description = "Низкая совместимость. Требуется большая работа."
        
        return {
            "score": round(normalized_score, 1),
            "level": level,
            "description": description,
            "positive_score": round(positive_score, 1),
            "negative_score": round(negative_score, 1),
            "neutral_score": round(neutral_score, 1),
            "total_score": round(total_score, 1)
        }
    
    @classmethod
    def _analyze_aspects(
        cls,
        aspects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Анализирует аспекты по категориям и типам планет.
        """
        analysis = {
            "harmonious": [],
            "challenging": [],
            "neutral": [],
            "by_planet": {}
        }
        
        aspect_categories = {
            'Conjunction': 'intense',
            'Opposition': 'challenging',
            'Square': 'challenging',
            'Trine': 'harmonious',
            'Sextile': 'harmonious',
            'Quincunx': 'neutral',
            'Semi-sextile': 'neutral',
            'Semi-square': 'challenging',
            'Sesquiquadrate': 'challenging',
        }
        
        for aspect in aspects:
            aspect_name = aspect.get('aspect', '')
            p1 = aspect.get('planet1', '')
            p2 = aspect.get('planet2', '')
            
            category = aspect_categories.get(aspect_name, 'neutral')
            
            # Добавляем в соответствующую категорию
            aspect_entry = f"{p1} {aspect_name} {p2} (орбис: {aspect['orbit']}°)"
            if category == 'harmonious':
                analysis['harmonious'].append(aspect_entry)
            elif category == 'challenging':
                analysis['challenging'].append(aspect_entry)
            else:
                analysis['neutral'].append(aspect_entry)
            
            # Группируем по планетам первого человека
            if p1 not in analysis['by_planet']:
                analysis['by_planet'][p1] = []
            analysis['by_planet'][p1].append(f"{p2} {aspect_name} (орбис: {aspect['orbit']}°)")
        
        # Подсчитываем статистику
        analysis['statistics'] = {
            "harmonious_count": len(analysis['harmonious']),
            "challenging_count": len(analysis['challenging']),
            "neutral_count": len(analysis['neutral']),
            "total_analyzed": len(aspects)
        }
        
        return analysis
    
    @classmethod
    def _find_strengths_and_weaknesses(
        cls,
        aspects: List[Dict[str, Any]]
    ) -> tuple:
        """
        Находит сильные и слабые стороны отношений.
        """
        strengths = []
        weaknesses = []
        
        # Анализируем аспекты для выявления сильных сторон
        for aspect in aspects:
            p1 = aspect.get('planet1', '')
            p2 = aspect.get('planet2', '')
            aspect_name = aspect.get('aspect', '')
            orbit = aspect.get('orbit', 10)
            
            # Сильные стороны (гармоничные аспекты с малым орбисом)
            if aspect_name in ['Trine', 'Sextile'] and orbit < 3:
                if p1 in ['Sun', 'Moon', 'Venus'] or p2 in ['Sun', 'Moon', 'Venus']:
                    strengths.append(f"Гармоничный {aspect_name} между {p1} и {p2} (орбис: {orbit}°)")
            
            # Слабые стороны (напряженные аспекты с малым орбисом)
            if aspect_name in ['Square', 'Opposition'] and orbit < 3:
                if p1 in ['Sun', 'Moon', 'Mars'] or p2 in ['Sun', 'Moon', 'Mars']:
                    weaknesses.append(f"Напряженный {aspect_name} между {p1} и {p2} (орбис: {orbit}°)")
        
        # Добавляем общие выводы, если списки пустые
        if not strengths:
            strengths.append("В карте нет ярко выраженных сильных аспектов.")
        if not weaknesses:
            weaknesses.append("В карте нет ярко выраженных слабых аспектов.")
        
        return strengths[:5], weaknesses[:5]
    
    @classmethod
    def _generate_report(
        cls,
        user1_data: Dict[str, Any],
        user2_data: Dict[str, Any],
        aspects: List[Dict[str, Any]],
        score: Dict[str, Any],
        analysis: Dict[str, Any],
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """
        Генерирует текстовый отчет о совместимости.
        """
        name1 = user1_data.get('first_name', 'User1')
        name2 = user2_data.get('first_name', 'User2')
        
        report = f"""
========================================
📊 ОТЧЕТ О СОВМЕСТИМОСТИ
========================================

👤 {name1} и {name2}

📈 ОБЩАЯ ОЦЕНКА
----------------------------------------
Балл совместимости: {score['score']}/100
Уровень: {score['level']}
{score['description']}

📊 СТАТИСТИКА АСПЕКТОВ
----------------------------------------
Всего аспектов: {len(aspects)}
Гармоничных: {analysis['statistics']['harmonious_count']}
Напряженных: {analysis['statistics']['challenging_count']}
Нейтральных: {analysis['statistics']['neutral_count']}

💪 СИЛЬНЫЕ СТОРОНЫ
----------------------------------------
"""
        for i, strength in enumerate(strengths, 1):
            report += f"{i}. {strength}\n"
        
        report += f"""
⚠️ СЛАБЫЕ СТОРОНЫ
----------------------------------------
"""
        for i, weakness in enumerate(weaknesses, 1):
            report += f"{i}. {weakness}\n"
        
        # Добавляем детали гармоничных аспектов
        if analysis['harmonious']:
            report += f"""
✨ ГАРМОНИЧНЫЕ АСПЕКТЫ
----------------------------------------
"""
            for aspect in analysis['harmonious'][:5]:
                report += f"  • {aspect}\n"
        
        # Добавляем детали напряженных аспектов
        if analysis['challenging']:
            report += f"""
⚡ НАПРЯЖЕННЫЕ АСПЕКТЫ
----------------------------------------
"""
            for aspect in analysis['challenging'][:5]:
                report += f"  • {aspect}\n"
        
        report += """
========================================
"""
        
        return report
    
    @classmethod
    def save_synastry_to_file(
        cls,
        synastry_data: Dict[str, Any],
        username1: str,
        username2: str,
        output_dir: Path,
        filename: Optional[str] = None
    ) -> Path:
        """
        Сохраняет данные синастрии в JSON файл.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"synastry_{username1}_{username2}_{date_str}.json"
        elif not filename.endswith('.json'):
            filename += '.json'
        
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(synastry_data, f, indent=4, ensure_ascii=False, default=str)
        
        logger.info(f"Синастрия сохранена в: {file_path}")
        return file_path