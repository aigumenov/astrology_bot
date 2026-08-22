#!/usr/bin/env python3
"""
Простой тест транзитов
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print(f"📁 Корневая папка: {root_dir}")
print(f"📋 PYTHONPATH добавлен: {str(root_dir)}")

try:
    print("\n🔮 Импортируем модули...")
    
    from storage.user_repository import UserRepository
    print("   ✅ UserRepository импортирован")
    
    from core.subject_factory import SubjectFactory
    print("   ✅ SubjectFactory импортирован")
    
    from core.aspects_calculator import AspectsCalculator
    print("   ✅ AspectsCalculator импортирован")
    
    from core.transits_calculator import TransitsCalculator
    print("   ✅ TransitsCalculator импортирован")
    
    print("\n👤 Загружаем пользователя...")
    user_repo = UserRepository()
    user_data = user_repo.load_user_data("drulya")
    
    if user_data:
        print(f"   ✅ Пользователь загружен: {user_data.get('username')}")
    else:
        print("   ❌ Пользователь не найден. Создайте пользователя через test_core.py")
        sys.exit(1)
    
    print("\n🧪 Рассчитываем транзиты...")
    transits = TransitsCalculator.calculate_current_transits(
        user_data=user_data,
        min_significance=2
    )
    
    print(f"\n✅ Транзиты рассчитаны!")
    print(f"   - Дата: {transits['transit_date']}")
    print(f"   - Всего аспектов: {transits['aspects']['total_all']}")
    print(f"   - Значимых аспектов: {transits['aspects']['total']}")
    
    if transits['aspects']['list']:
        print(f"\n   📊 Первые 3 аспекта:")
        for i, aspect in enumerate(transits['aspects']['list'][:3]):
            print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)")
    
    print("\n🎉 Тест успешно завершен!")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()