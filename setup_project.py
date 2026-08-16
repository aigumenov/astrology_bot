import os
from pathlib import Path

# Базовая структура
DIRS = [
    "bot",
    "handlers",
    "keyboards",
    "states",
    "core",
    "analysis",
    "business",
    "storage",
    "infrastructure",
    "data/user_data",
    "data/prompts",
    "tests/test_core",
    "tests/test_analysis",
    "tests/test_handlers",
]

# Файлы, которые должны быть созданы
FILES = [
    "bot/main.py",
    "bot/dispatcher.py",
    "bot/scheduler.py",
    ".env",
    "requirements.txt",
    "Dockerfile",
    "README.md",
    "handlers/commands.py",
    "handlers/onboarding.py",
    "handlers/natal_handlers.py",
    "handlers/forecast_handlers.py",
    "handlers/synastry_handlers.py",
    "handlers/settings_handlers.py",
    "handlers/payment_handlers.py",
    "keyboards/main_menu.py",
    "keyboards/inline_buttons.py",
    "keyboards/tariffs.py",
    "states/natal_states.py",
    "states/synastry_states.py",
    "core/subject_factory.py",
    "core/natal_calculator.py",
    "core/aspects_calculator.py",
    "core/transits_calculator.py",
    "core/synastry_calculator.py",
    "core/composite_calculator.py",
    "core/returns_calculator.py",
    "core/ephemeris_generator.py",
    "core/chart_drawer.py",
    "analysis/context_builder.py",
    "analysis/prompt_templates.py",
    "analysis/llm_client.py",
    "analysis/profile_generator.py",
    "analysis/recommendation_engine.py",
    "analysis/report_generator.py",
    "analysis/report_formatter.py",
    "business/tariffs.py",
    "business/subscriptions.py",
    "business/payments.py",
    "business/request_counter.py",
    "business/bonuses.py",
    "business/analytics.py",
    "storage/user_repository.py",
    "storage/chart_repository.py",
    "storage/session_manager.py",
    "storage/cache_manager.py",
    "storage/geocode_cache.py",
    "infrastructure/config.py",
    "infrastructure/logging.py",
    "infrastructure/i18n.py",
    "infrastructure/file_manager.py",
    "infrastructure/image_converter.py",
    "infrastructure/export_service.py",
    "data/prompts/profile.yaml",
    "data/prompts/forecast.yaml",
    "data/prompts/synastry.yaml",
]

def create_project_structure():
    """Создает структуру каталогов и файлов проекта"""
    print("🚀 Создание структуры проекта...")
    
    # Создаем базовую папку
    root = Path("astrology_bot")
    root.mkdir(exist_ok=True)
    
    # Создаем все папки
    for dir_path in DIRS:
        (root / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  📁 Создана папка: {dir_path}")
    
    # Создаем __init__.py во всех папках
    for dir_path in DIRS:
        init_file = root / dir_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"  📄 Создан: {dir_path}/__init__.py")
    
    # Создаем остальные файлы
    for file_path in FILES:
        file_full_path = root / file_path
        if not file_full_path.exists():
            file_full_path.touch()
            print(f"  📄 Создан: {file_path}")
    
    print("\n✅ Структура проекта создана успешно!")
    print(f"📁 Корневая папка: {root.absolute()}")

if __name__ == "__main__":
    create_project_structure()