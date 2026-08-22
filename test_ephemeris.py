#!/usr/bin/env python3
"""
Тестовый скрипт для проверки модуля эфемерид

Запуск: python test_ephemeris.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from core.ephemeris_generator import EphemerisGenerator


def test_daily_ephemeris():
    """Тест 1: Ежедневные эфемериды (7 дней)"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 1: Ежедневные эфемериды (7 дней)")
    print("=" * 60)
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    try:
        ephemeris = EphemerisGenerator.generate_daily_ephemeris(
            start_date=start_date,
            end_date=end_date,
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow"
        )
        
        print(f"✅ Эфемериды сгенерированы")
        print(f"   - Период: {ephemeris['period']['start_date']} - {ephemeris['period']['end_date']}")
        print(f"   - Всего дней: {ephemeris['period']['total_days']}")
        print(f"   - Планет в дне: {len(ephemeris['days'][0]['planets']) if ephemeris['days'] else 0}")
        
        if ephemeris['days']:
            first_day = ephemeris['days'][0]
            print(f"\n   📊 Пример данных на {first_day['date']}:")
            for planet in first_day['planets'][:5]:
                print(f"      {planet['name']}: {planet['sign']} {planet['degree']}° "
                      f"({planet['abs_pos']}°)")
        
        # Сохраняем
        output_dir = Path("test_output")
        file_path = EphemerisGenerator.save_ephemeris_to_file(
            ephemeris_data=ephemeris,
            filename="ephemeris_daily_7days.json",
            output_dir=output_dir
        )
        print(f"\n💾 Эфемериды сохранены: {file_path}")
        
        return ephemeris
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_hourly_ephemeris():
    """Тест 2: Почасовые эфемериды (1 день)"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 2: Почасовые эфемериды (1 день, шаг 3 часа)")
    print("=" * 60)
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    try:
        ephemeris = EphemerisGenerator.generate_hourly_ephemeris(
            start_date=start_date,
            end_date=end_date,
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow",
            step_hours=3
        )
        
        print(f"✅ Почасовые эфемериды сгенерированы")
        print(f"   - Период: {ephemeris['period']['start_date']} - {ephemeris['period']['end_date']}")
        print(f"   - Всего точек: {ephemeris['period']['total_days']}")
        
        if ephemeris['days']:
            print(f"\n   📊 Первые 3 точки:")
            for day in ephemeris['days'][:3]:
                print(f"      {day['date']}: {len(day['planets'])} планет")
        
        output_dir = Path("test_output")
        file_path = EphemerisGenerator.save_ephemeris_to_file(
            ephemeris_data=ephemeris,
            filename="ephemeris_hourly_1day.json",
            output_dir=output_dir
        )
        print(f"\n💾 Эфемериды сохранены: {file_path}")
        
        return ephemeris
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_planet_positions_on_date():
    """Тест 3: Положения планет на конкретную дату"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 3: Положения планет на конкретную дату")
    print("=" * 60)
    
    target_date = datetime.now() + timedelta(days=30)
    
    try:
        positions = EphemerisGenerator.get_planet_positions_on_date(
            target_date=target_date,
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow"
        )
        
        print(f"✅ Положения планет на {target_date.strftime('%Y-%m-%d')}")
        print(f"   - Всего планет: {len(positions['positions'])}")
        
        print(f"\n   📊 Положения планет:")
        for name, data in list(positions['positions'].items())[:10]:
            retro = " (ретроградная)" if data['retrograde'] else ""
            print(f"      {name}: {data['sign']} {data['degree']}°{retro}")
        
        # Сохраняем
        output_dir = Path("test_output")
        file_path = EphemerisGenerator.save_ephemeris_to_file(
            ephemeris_data=positions,
            filename=f"planets_{target_date.strftime('%Y%m%d')}.json",
            output_dir=output_dir
        )
        print(f"\n💾 Данные сохранены: {file_path}")
        
        return positions
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_ephemeris_for_transits():
    """Тест 4: Эфемериды для транзитов (30 дней)"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 4: Эфемериды для транзитов (30 дней)")
    print("=" * 60)
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    try:
        ephemeris = EphemerisGenerator.generate_ephemeris_for_date_range(
            start_date=start_date,
            end_date=end_date,
            step_type="days",
            step=1,
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow"
        )
        
        print(f"✅ Эфемериды для транзитов сгенерированы")
        print(f"   - Период: {ephemeris['period']['start_date']} - {ephemeris['period']['end_date']}")
        print(f"   - Всего дней: {ephemeris['period']['total_days']}")
        
        # Анализируем движение планет
        if ephemeris['days']:
            print(f"\n   📊 Движение планет за период:")
            
            # Собираем данные по каждой планете
            planet_data = {}
            for day in ephemeris['days']:
                for planet in day['planets']:
                    name = planet['name']
                    if name not in planet_data:
                        planet_data[name] = {
                            'start': planet['degree'],
                            'end': planet['degree'],
                            'days': 1
                        }
                    else:
                        planet_data[name]['end'] = planet['degree']
                        planet_data[name]['days'] += 1
            
            # Выводим изменение
            for name, data in list(planet_data.items())[:5]:
                diff = abs(data['end'] - data['start'])
                direction = "вперед" if data['end'] > data['start'] else "назад"
                if diff > 20:
                    # Учитываем переход через 0°
                    diff = 360 - diff
                print(f"      {name}: изменилась на {diff:.2f}° (движение {direction})")
        
        output_dir = Path("test_output")
        file_path = EphemerisGenerator.save_ephemeris_to_file(
            ephemeris_data=ephemeris,
            filename="ephemeris_transits_30days.json",
            output_dir=output_dir
        )
        print(f"\n💾 Эфемериды сохранены: {file_path}")
        
        return ephemeris
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_custom_range_ephemeris():
    """Тест 5: Эфемериды с кастомным диапазоном (7 дней, шаг 2 дня)"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ 5: Эфемериды с шагом 2 дня (7 дней)")
    print("=" * 60)
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    try:
        ephemeris = EphemerisGenerator.generate_ephemeris_for_date_range(
            start_date=start_date,
            end_date=end_date,
            step_type="days",
            step=2,
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow"
        )
        
        print(f"✅ Эфемериды с шагом 2 дня сгенерированы")
        print(f"   - Период: {ephemeris['period']['start_date']} - {ephemeris['period']['end_date']}")
        print(f"   - Всего точек: {ephemeris['period']['total_days']}")
        print(f"   - Ожидалось: 4 точки (дни 0, 2, 4, 6)")
        
        if ephemeris['days']:
            print(f"\n   📊 Точки:")
            for day in ephemeris['days']:
                print(f"      {day['date']}: {len(day['planets'])} планет")
        
        output_dir = Path("test_output")
        file_path = EphemerisGenerator.save_ephemeris_to_file(
            ephemeris_data=ephemeris,
            filename="ephemeris_step2_7days.json",
            output_dir=output_dir
        )
        print(f"\n💾 Эфемериды сохранены: {file_path}")
        
        return ephemeris
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ МОДУЛЯ ЭФЕМЕРИД")
    print("=" * 60)
    
    print("\nℹ️ Генерация эфемерид для различных периодов и шагов.")
    
    test_daily_ephemeris()
    test_hourly_ephemeris()
    test_planet_positions_on_date()
    test_ephemeris_for_transits()
    test_custom_range_ephemeris()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)


if __name__ == "__main__":
    main()