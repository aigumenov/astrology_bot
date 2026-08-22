#!/usr/bin/env python3
"""
Диагностический скрипт для проверки импортов и структуры проекта
"""

import sys
from pathlib import Path

print("=" * 60)
print("🔍 ДИАГНОСТИКА ПРОЕКТА")
print("=" * 60)

# 1. Проверяем текущую директорию
print(f"\n📁 Текущая директория: {Path.cwd()}")

# 2. Проверяем PYTHONPATH
print(f"\n📋 PYTHONPATH: {sys.path}")

# 3. Проверяем наличие модулей
modules_to_check = [
    "core",
    "core.subject_factory",
    "core.aspects_calculator",
    "core.transits_calculator",
    "storage",
    "storage.user_repository"
]

print("\n📦 Проверка импортов:")
for module_name in modules_to_check:
    try:
        module = __import__(module_name)
        if '.' in module_name:
            # Проверяем вложенный модуль
            parts = module_name.split('.')
            for part in parts[1:]:
                module = getattr(module, part)
        print(f"   ✅ {module_name} - найден")
    except ImportError as e:
        print(f"   ❌ {module_name} - НЕ НАЙДЕН: {e}")

# 4. Проверяем наличие файлов пользователя
print("\n👤 Проверка пользователей:")
user_data_dir = Path("data/user_data")
if user_data_dir.exists():
    users = [d for d in user_data_dir.iterdir() if d.is_dir()]
    if users:
        print(f"   Найдены пользователи: {', '.join([u.name for u in users])}")
        for user in users:
            user_file = user / f"{user.name}.json"
            if user_file.exists():
                print(f"   ✅ {user.name}: {user_file} (существует)")
            else:
                print(f"   ⚠️ {user.name}: {user_file} (НЕ НАЙДЕН)")
    else:
        print("   ❌ Пользователи не найдены")
else:
    print(f"   ❌ Папка {user_data_dir} не существует")

# 5. Проверяем kerykeion
print("\n🔮 Проверка Kerykeion:")
try:
    import kerykeion
    print(f"   ✅ Kerykeion установлен (версия: {kerykeion.__version__})")
except ImportError:
    print("   ❌ Kerykeion НЕ УСТАНОВЛЕН")
except AttributeError:
    print("   ✅ Kerykeion установлен (версия неизвестна)")

print("\n" + "=" * 60)
print("🎯 Диагностика завершена")
print("=" * 60)