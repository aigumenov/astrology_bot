#!/usr/bin/env python3
"""
Тестовый скрипт для проверки транзитов

Запуск: python test_transits.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from core.transits_calculator import TransitsCalculator
from storage.user_repository import UserRepository


def test_current_transits():
    """Тест 1: Текущие транзиты"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 1: Текущие транзиты")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден. Сначала запустите test_core.py")
        return
    
    try:
        transits = TransitsCalculator.calculate_current_transits(
            user_data=user_data,
            min_significance=2
        )
        
        print(f"✅ Транзиты рассчитаны")
        print(f"   - Дата: {transits['transit_date']}")
        print(f"   - Всего аспектов: {transits['aspects']['total_all']}")
        print(f"   - Значимых аспектов: {transits['aspects']['total']}")
        print(f"   - Оценка дня: {transits['day_score']['overall']} ({transits['day_score']['level']})")
        print(f"   - Сводка: {transits['summary']}")
        
        if transits['aspects']['list']:
            print(f"\n   📊 Значимые аспекты:")
            for i, aspect in enumerate(transits['aspects']['list'][:5]):
                print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} "
                      f"(орбис: {aspect['orbit']}°)")
        
        user_dir = user_repo.get_user_dir("drulya")
        file_path = TransitsCalculator.save_transits_to_file(
            transits_data=transits,
            username="drulya",
            output_dir=user_dir,
            filename="drulya_transits_current.json"
        )
        print(f"\n💾 Транзиты сохранены: {file_path}")
        
        return transits
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_transits_for_date():
    """Тест 2: Транзиты на конкретную дату"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 2: Транзиты на конкретную дату")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден")
        return
    
    target_date = datetime.now() + timedelta(days=7)
    
    try:
        transits = TransitsCalculator.calculate_transits_for_date(
            user_data=user_data,
            target_date=target_date,
            min_significance=2
        )
        
        print(f"✅ Транзиты на {target_date.strftime('%Y-%m-%d')}")
        
        if 'aspects' in transits:
            if 'total_all' in transits['aspects']:
                print(f"   - Всего аспектов: {transits['aspects']['total_all']}")
            else:
                print(f"   - Всего аспектов: {len(transits['aspects'].get('list', []))}")
            print(f"   - Значимых аспектов: {transits['aspects']['total']}")
        
        if 'day_score' in transits:
            print(f"   - Оценка дня: {transits['day_score']['overall']} ({transits['day_score']['level']})")
        
        if 'summary' in transits:
            print(f"   - Сводка: {transits['summary']}")
        
        if 'aspects' in transits and transits['aspects'].get('list'):
            aspects_list = transits['aspects']['list']
            print(f"\n   📊 Значимые аспекты:")
            for i, aspect in enumerate(aspects_list[:5]):
                print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} "
                      f"(орбис: {aspect['orbit']}°)")
        
        user_dir = user_repo.get_user_dir("drulya")
        file_path = TransitsCalculator.save_transits_to_file(
            transits_data=transits,
            username="drulya",
            output_dir=user_dir,
            filename=f"drulya_transits_{target_date.strftime('%Y%m%d')}.json"
        )
        print(f"\n💾 Транзиты сохранены: {file_path}")
        
        return transits
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_transits_period():
    """Тест 3: Транзиты за период (14 дней)"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 3: Транзиты за период (14 дней)")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден")
        return
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)
    
    try:
        transits = TransitsCalculator.calculate_transits_period(
            user_data=user_data,
            start_date=start_date,
            end_date=end_date,
            step_days=1,
            min_significance=2
        )
        
        print(f"✅ Транзиты за период рассчитаны")
        print(f"   - Период: {transits['period']['start_date']} - {transits['period']['end_date']}")
        print(f"   - Всего дней: {transits['period']['total_days']}")
        print(f"   - Дней с транзитами: {transits['statistics']['days_with_aspects']}")
        print(f"   - Среднее аспектов в день: {transits['statistics']['avg_aspects_per_day']}")
        
        if transits['significant_days']:
            print(f"\n   📊 Самые значимые дни:")
            for i, day in enumerate(transits['significant_days'][:3]):
                print(f"      {i+1}. {day['date']} — {day['aspects_count']} аспектов")
        
        user_dir = user_repo.get_user_dir("drulya")
        file_path = TransitsCalculator.save_transits_to_file(
            transits_data=transits,
            username="drulya",
            output_dir=user_dir,
            filename="drulya_transits_period.json"
        )
        print(f"\n💾 Транзиты сохранены: {file_path}")
        
        return transits
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ МОДУЛЯ ТРАНЗИТОВ")
    print("=" * 60)
    
    test_current_transits()
    test_transits_for_date()
    test_transits_period()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()