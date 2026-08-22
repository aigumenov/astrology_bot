#!/usr/bin/env python3
"""
Тестовый скрипт для проверки модуля возвращений (Solar & Lunar Returns)

Запуск: python test_returns.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from core.returns_calculator import ReturnsCalculator
from storage.user_repository import UserRepository


def test_solar_return():
    """Тест 1: Солярное возвращение"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 1: Солярное возвращение")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден. Сначала запустите test_core.py")
        return
    
    # Рассчитываем солярное возвращение на следующий год
    current_year = datetime.now().year
    target_year = current_year + 1
    
    try:
        solar_return = ReturnsCalculator.calculate_solar_return(
            user_data=user_data,
            year=target_year,
            city="Moscow"
        )
        
        print(f"✅ Солярное возвращение на {target_year} год")
        print(f"   - Дата: {solar_return['return_date']}")
        print(f"   - Асцендент: {solar_return['ascendant']['sign']} ({solar_return['ascendant']['degree']}°)")
        print(f"   - Всего аспектов: {solar_return['aspects']['total']}")
        print(f"   - Сводка: {solar_return['summary']}")
        
        if solar_return['aspects']['list']:
            print(f"\n   📊 Первые 5 аспектов:")
            for i, aspect in enumerate(solar_return['aspects']['list'][:5]):
                print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} "
                      f"(орбис: {aspect['orbit']}°)")
        
        # Сохраняем
        user_dir = user_repo.get_user_dir("drulya")
        file_path = ReturnsCalculator.save_return_to_file(
            return_data=solar_return,
            username="drulya",
            output_dir=user_dir
        )
        print(f"\n💾 Данные сохранены: {file_path}")
        
        return solar_return
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_lunar_return():
    """Тест 2: Лунное возвращение"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 2: Лунное возвращение")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден")
        return
    
    try:
        lunar_return = ReturnsCalculator.calculate_next_lunar_return(
            user_data=user_data,
            city="Moscow"
        )
        
        print(f"✅ Следующее лунное возвращение")
        print(f"   - Дата: {lunar_return['return_date']}")
        print(f"   - Асцендент: {lunar_return['ascendant']['sign']} ({lunar_return['ascendant']['degree']}°)")
        print(f"   - Всего аспектов: {lunar_return['aspects']['total']}")
        print(f"   - Сводка: {lunar_return['summary']}")
        
        if lunar_return['aspects']['list']:
            print(f"\n   📊 Первые 5 аспектов:")
            for i, aspect in enumerate(lunar_return['aspects']['list'][:5]):
                print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} "
                      f"(орбис: {aspect['orbit']}°)")
        
        # Сохраняем
        user_dir = user_repo.get_user_dir("drulya")
        file_path = ReturnsCalculator.save_return_to_file(
            return_data=lunar_return,
            username="drulya",
            output_dir=user_dir
        )
        print(f"\n💾 Данные сохранены: {file_path}")
        
        return lunar_return
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_multiple_lunar_returns():
    """Тест 3: Несколько лунных возвращений"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 3: Несколько лунных возвращений (3 месяца)")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден")
        return
    
    try:
        returns = ReturnsCalculator.calculate_multiple_lunar_returns(
            user_data=user_data,
            count=3,
            city="Moscow"
        )
        
        print(f"✅ {returns['count']} лунных возвращений рассчитаны")
        print(f"   - Местоположение: {returns['location']['city']}")
        
        for i, return_data in enumerate(returns['returns'], 1):
            print(f"\n   📅 Лунное возвращение #{i}:")
            print(f"      - Дата: {return_data['return_date']}")
            print(f"      - Аспектов: {return_data['aspects']['total']}")
            print(f"      - Сводка: {return_data['summary']}")
        
        # Сохраняем
        user_dir = user_repo.get_user_dir("drulya")
        file_path = ReturnsCalculator.save_return_to_file(
            return_data=returns,
            username="drulya",
            output_dir=user_dir,
            filename=f"drulya_lunar_returns_multiple.json"
        )
        print(f"\n💾 Данные сохранены: {file_path}")
        
        return returns
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_compare_returns():
    """Тест 4: Сравнение солнечного и лунного возвращения"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 4: Сравнение возвращений")
    print("=" * 60)
    
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if not user_data:
        print("❌ Пользователь не найден")
        return
    
    current_year = datetime.now().year
    target_year = current_year + 1
    
    try:
        # Солнечное возвращение
        solar = ReturnsCalculator.calculate_solar_return(
            user_data=user_data,
            year=target_year,
            city="Moscow"
        )
        
        # Лунное возвращение
        lunar = ReturnsCalculator.calculate_next_lunar_return(
            user_data=user_data,
            city="Moscow"
        )
        
        print(f"✅ Сравнение возвращений")
        print(f"\n   ☀️ Солярное возвращение на {target_year} год:")
        print(f"      - Дата: {solar['return_date']}")
        print(f"      - Асцендент: {solar['ascendant']['sign']} ({solar['ascendant']['degree']}°)")
        print(f"      - Аспектов: {solar['aspects']['total']}")
        print(f"      - Сводка: {solar['summary']}")
        
        print(f"\n   🌙 Лунное возвращение:")
        print(f"      - Дата: {lunar['return_date']}")
        print(f"      - Асцендент: {lunar['ascendant']['sign']} ({lunar['ascendant']['degree']}°)")
        print(f"      - Аспектов: {lunar['aspects']['total']}")
        print(f"      - Сводка: {lunar['summary']}")
        
        # Сравнение
        print(f"\n   📊 Сравнение:")
        solar_aspects = solar['aspects']['total']
        lunar_aspects = lunar['aspects']['total']
        
        if solar_aspects > lunar_aspects:
            print(f"      - Солнечное возвращение более насыщенное ({solar_aspects} > {lunar_aspects} аспектов)")
        elif lunar_aspects > solar_aspects:
            print(f"      - Лунное возвращение более насыщенное ({lunar_aspects} > {solar_aspects} аспектов)")
        else:
            print(f"      - Оба возвращения имеют одинаковое количество аспектов ({solar_aspects})")
        
        return solar, lunar
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ МОДУЛЯ ВОЗВРАЩЕНИЙ")
    print("=" * 60)
    
    print("\nℹ️ Для расчета солярного возвращения используется следующий год.")
    print("ℹ️ Для расчета лунного возвращения используется текущая дата.")
    
    test_solar_return()
    test_lunar_return()
    test_multiple_lunar_returns()
    test_compare_returns()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()