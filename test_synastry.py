#!/usr/bin/env python3
"""
Тестовый скрипт для проверки модуля синастрии

Запуск: python test_synastry.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from core.synastry_calculator import SynastryCalculator
from storage.user_repository import UserRepository


def test_synastry_by_username():
    """Тест 1: Расчет синастрии по именам пользователей"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 1: Синастрия по именам пользователей")
    print("=" * 60)
    
    user_repo = UserRepository()
    
    # Проверяем наличие пользователей
    username1 = "andrey_igumenov"
    username2 = "drulya"
    
    user1 = user_repo.load_user_data(username1)
    user2 = user_repo.load_user_data(username2)
    
    if not user1:
        print(f"❌ Пользователь {username1} не найден")
        return
    if not user2:
        print(f"❌ Пользователь {username2} не найден")
        return
    
    try:
        synastry = SynastryCalculator.calculate_synastry(
            user1_data=user1,
            user2_data=user2,
            include_minor_aspects=False,
            min_significance=2
        )
        
        print(f"✅ Синастрия рассчитана")
        print(f"   - {username1} и {username2}")
        print(f"   - Всего аспектов: {synastry['aspects']['total']}")
        print(f"   - Значимых аспектов: {synastry['aspects']['filtered']}")
        print(f"   - Балл совместимости: {synastry['compatibility_score']['score']}/100")
        print(f"   - Уровень: {synastry['compatibility_score']['level']}")
        print(f"   - Описание: {synastry['compatibility_score']['description']}")
        
        print(f"\n   💪 Сильные стороны:")
        for strength in synastry['strengths'][:3]:
            print(f"      • {strength}")
        
        print(f"\n   ⚠️ Слабые стороны:")
        for weakness in synastry['weaknesses'][:3]:
            print(f"      • {weakness}")
        
        # Сохраняем
        user_dir = user_repo.get_user_dir("synastry")
        file_path = SynastryCalculator.save_synastry_to_file(
            synastry_data=synastry,
            username1=username1,
            username2=username2,
            output_dir=user_dir
        )
        print(f"\n💾 Данные сохранены: {file_path}")
        
        # Показываем отчет
        print(f"\n📄 ОТЧЕТ О СОВМЕСТИМОСТИ:")
        print(synastry['report'])
        
        return synastry
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_synastry_with_minor_aspects():
    """Тест 2: Синастрия с второстепенными аспектами"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 2: Синастрия с второстепенными аспектами")
    print("=" * 60)
    
    user_repo = UserRepository()
    
    username1 = "andrey_igumenov"
    username2 = "drulya"
    
    user1 = user_repo.load_user_data(username1)
    user2 = user_repo.load_user_data(username2)
    
    if not user1 or not user2:
        print("❌ Пользователи не найдены")
        return
    
    try:
        synastry = SynastryCalculator.calculate_synastry(
            user1_data=user1,
            user2_data=user2,
            include_minor_aspects=True,
            min_significance=1
        )
        
        print(f"✅ Синастрия с второстепенными аспектами")
        print(f"   - Всего аспектов: {synastry['aspects']['total']}")
        print(f"   - Значимых аспектов: {synastry['aspects']['filtered']}")
        print(f"   - Балл совместимости: {synastry['compatibility_score']['score']}/100")
        
        print(f"\n   📊 Статистика:")
        stats = synastry['analysis']['statistics']
        print(f"      Гармоничных: {stats['harmonious_count']}")
        print(f"      Напряженных: {stats['challenging_count']}")
        print(f"      Нейтральных: {stats['neutral_count']}")
        
        return synastry
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_synastry_detailed_analysis():
    """Тест 3: Детальный анализ синастрии"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 3: Детальный анализ синастрии")
    print("=" * 60)
    
    user_repo = UserRepository()
    
    username1 = "andrey_igumenov"
    username2 = "drulya"
    
    user1 = user_repo.load_user_data(username1)
    user2 = user_repo.load_user_data(username2)
    
    if not user1 or not user2:
        print("❌ Пользователи не найдены")
        return
    
    try:
        synastry = SynastryCalculator.calculate_synastry(
            user1_data=user1,
            user2_data=user2,
            include_minor_aspects=False,
            min_significance=2
        )
        
        print(f"✅ Детальный анализ")
        
        # Анализ по планетам
        print(f"\n   📊 Аспекты по планетам:")
        for planet, aspects in synastry['analysis']['by_planet'].items():
            print(f"      {planet}: {len(aspects)} аспектов")
            for aspect in aspects[:3]:
                print(f"         • {aspect}")
        
        # Показываем гармоничные аспекты
        print(f"\n   ✨ Гармоничные аспекты ({len(synastry['analysis']['harmonious'])}):")
        for aspect in synastry['analysis']['harmonious'][:5]:
            print(f"      • {aspect}")
        
        # Показываем напряженные аспекты
        print(f"\n   ⚡ Напряженные аспекты ({len(synastry['analysis']['challenging'])}):")
        for aspect in synastry['analysis']['challenging'][:5]:
            print(f"      • {aspect}")
        
        return synastry
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_synastry_by_direct_input():
    """Тест 4: Синастрия с прямым вводом данных"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 4: Синастрия с прямым вводом данных")
    print("=" * 60)
    
    # Данные для теста (можно заменить на свои)
    user1_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "username": "alice_smith",
        "birth_date": "15-07-1990",
        "birth_time": "10-30",
        "latitude": 51.5074,
        "longitude": -0.1276,
        "timezone": "Europe/London"
    }
    
    user2_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "username": "bob_johnson",
        "birth_date": "22-03-1988",
        "birth_time": "14-00",
        "latitude": 51.5074,
        "longitude": -0.1276,
        "timezone": "Europe/London"
    }
    
    try:
        synastry = SynastryCalculator.calculate_synastry(
            user1_data=user1_data,
            user2_data=user2_data,
            include_minor_aspects=False,
            min_significance=2
        )
        
        print(f"✅ Синастрия для тестовых данных")
        print(f"   - {user1_data['first_name']} и {user2_data['first_name']}")
        print(f"   - Балл совместимости: {synastry['compatibility_score']['score']}/100")
        print(f"   - Уровень: {synastry['compatibility_score']['level']}")
        
        return synastry
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ МОДУЛЯ СИНАСТРИИ")
    print("=" * 60)
    
    print("\nℹ️ Для тестов используются пользователи:")
    print("   - andrey_igumenov (первый пользователь)")
    print("   - drulya (второй пользователь)")
    
    test_synastry_by_username()
    test_synastry_with_minor_aspects()
    test_synastry_detailed_analysis()
    test_synastry_by_direct_input()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()