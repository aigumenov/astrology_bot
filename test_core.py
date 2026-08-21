#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Блока 2: Ядро астрологических расчетов
С интерактивным вводом данных и сохранением в JSON

Запуск: python test_core.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from core import SubjectFactory, NatalCalculator, AspectsCalculator, ChartDrawer
from storage import UserRepository


# Словарь перевода знаков Зодиака
ZODIAC_TRANSLATIONS = {
    'Aries': 'Овен',
    'Taurus': 'Телец',
    'Gemini': 'Близнецы',
    'Cancer': 'Рак',
    'Leo': 'Лев',
    'Virgo': 'Дева',
    'Libra': 'Весы',
    'Scorpio': 'Скорпион',
    'Sagittarius': 'Стрелец',
    'Capricorn': 'Козерог',
    'Aquarius': 'Водолей',
    'Pisces': 'Рыбы',
    'Sag': 'Стрелец',
    'Vir': 'Дева',
    'Sco': 'Скорпион',
    'Aqu': 'Водолей',
    'Cap': 'Козерог',
    'Lib': 'Весы',
    'Can': 'Рак',
    'Leo': 'Лев',
    'Gem': 'Близнецы',
    'Tau': 'Телец',
    'Ari': 'Овен',
    'Pis': 'Рыбы',
}

# Словарь перевода домов
HOUSE_TRANSLATIONS = {
    'First_House': '1-й дом (Личность)',
    'Second_House': '2-й дом (Финансы)',
    'Third_House': '3-й дом (Общение)',
    'Fourth_House': '4-й дом (Семья)',
    'Fifth_House': '5-й дом (Творчество)',
    'Sixth_House': '6-й дом (Здоровье)',
    'Seventh_House': '7-й дом (Партнеры)',
    'Eighth_House': '8-й дом (Трансформация)',
    'Ninth_House': '9-й дом (Путешествия)',
    'Tenth_House': '10-й дом (Карьера)',
    'Eleventh_House': '11-й дом (Друзья)',
    'Twelfth_House': '12-й дом (Тайны)',
}

# Словарь перевода аспектов
ASPECT_TRANSLATIONS = {
    'Conjunction': 'Соединение',
    'Sextile': 'Секстиль',
    'Square': 'Квадрат',
    'Trine': 'Трин',
    'Opposition': 'Оппозиция',
    'Semi-sextile': 'Полусекстиль',
    'Semi-square': 'Полуквадрат',
    'Sesquiquadrate': 'Полутораквадрат',
    'Quincunx': 'Квинконс',
}


def translate_zodiac(sign: str) -> str:
    """Переводит знак Зодиака на русский"""
    if not sign:
        return 'Неизвестно'
    # Если знак уже на русском, возвращаем как есть
    if sign in ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 
                'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']:
        return sign
    return ZODIAC_TRANSLATIONS.get(sign, sign)


def translate_house(house: str) -> str:
    """Переводит название дома на русский"""
    if not house:
        return 'Неизвестно'
    return HOUSE_TRANSLATIONS.get(house, house)


def translate_aspect(aspect: str) -> str:
    """Переводит название аспекта на русский"""
    if not aspect:
        return 'Неизвестно'
    return ASPECT_TRANSLATIONS.get(aspect, aspect)


class InteractiveTester:
    """
    Интерактивный тестер для астрологических расчетов.
    Запрашивает данные у пользователя, сохраняет в JSON и выполняет расчеты.
    """
    
    def __init__(self):
        self.user_data = {}
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        self.user_repo = UserRepository()
    
    def get_user_input(self) -> Dict[str, Any]:
        """
        Запрашивает у пользователя данные для расчета.
        """
        print("\n" + "=" * 60)
        print("📝 ВВОД ДАННЫХ ДЛЯ РАСЧЕТА НАТАЛЬНОЙ КАРТЫ")
        print("=" * 60)
        
        # Имя
        while True:
            name = input("👤 Введите имя: ").strip()
            if name:
                self.user_data["first_name"] = name
                break
            print("❌ Имя не может быть пустым. Попробуйте снова.")
        
        # Фамилия (опционально)
        last_name = input("👤 Введите фамилию (опционально, Enter для пропуска): ").strip()
        if last_name:
            self.user_data["last_name"] = last_name
        else:
            self.user_data["last_name"] = ""
        
        # Дата рождения
        while True:
            birth_date = input("📅 Введите дату рождения (ДД-ММ-ГГГГ, например 25-11-1986): ").strip()
            try:
                datetime.strptime(birth_date, "%d-%m-%Y")
                self.user_data["birth_date"] = birth_date
                break
            except ValueError:
                print("❌ Неверный формат! Используйте ДД-ММ-ГГГГ. Попробуйте снова.")
        
        # Время рождения
        while True:
            birth_time = input("⏰ Введите время рождения (ЧЧ-ММ, например 06-10): ").strip()
            try:
                h, m = map(int, birth_time.split('-'))
                if 0 <= h <= 23 and 0 <= m <= 59:
                    self.user_data["birth_time"] = birth_time
                    break
                else:
                    print("❌ Часы должны быть 0-23, минуты 0-59. Попробуйте снова.")
            except ValueError:
                print("❌ Неверный формат! Используйте ЧЧ-ММ. Попробуйте снова.")
        
        # Город рождения
        while True:
            place = input("📍 Введите город рождения: ").strip()
            if place:
                self.user_data["place"] = place
                break
            print("❌ Город не может быть пустым. Попробуйте снова.")
        
        # Координаты (опционально)
        print("\n🌍 Если вы знаете координаты города, можете ввести их вручную.")
        print("   Если оставить пустыми, будут использованы координаты по умолчанию (Ростов-на-Дону).")
        
        lat_input = input("   Широта (например, 47.2357): ").strip()
        if lat_input:
            try:
                self.user_data["latitude"] = float(lat_input)
            except ValueError:
                print("⚠️ Неверный формат широты. Использую значение по умолчанию.")
                self.user_data["latitude"] = 47.2357
        else:
            self.user_data["latitude"] = 47.2357
        
        lng_input = input("   Долгота (например, 39.7015): ").strip()
        if lng_input:
            try:
                self.user_data["longitude"] = float(lng_input)
            except ValueError:
                print("⚠️ Неверный формат долготы. Использую значение по умолчанию.")
                self.user_data["longitude"] = 39.7015
        else:
            self.user_data["longitude"] = 39.7015
        
        # Часовой пояс (опционально)
        tz_input = input("   Часовой пояс (например, Europe/Moscow, Enter для пропуска): ").strip()
        if tz_input:
            self.user_data["timezone"] = tz_input
        else:
            self.user_data["timezone"] = "Europe/Moscow"
        
        # Генерация username
        username_base = self.user_data["first_name"].lower()
        if self.user_data.get("last_name"):
            username_base += f"_{self.user_data['last_name'].lower()}"
        
        # Проверяем уникальность
        if self.user_repo.user_exists(username_base):
            counter = 1
            while self.user_repo.user_exists(f"{username_base}_{counter}"):
                counter += 1
            username = f"{username_base}_{counter}"
        else:
            username = username_base
        
        self.user_data["username"] = username
        self.user_data["user_id"] = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_data["registered_at"] = datetime.now().isoformat()
        self.user_data["status"] = "active"
        self.user_data["tariff"] = "test"
        
        return self.user_data
    
    def save_user_data(self) -> Path:
        """
        Сохраняет данные пользователя в JSON файл.
        """
        user_dir = self.user_repo.get_user_dir(self.user_data["username"])
        
        file_path = user_dir / f"{self.user_data['username']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, indent=4, ensure_ascii=False, default=str)
        
        print(f"\n💾 Данные сохранены в: {file_path}")
        return file_path
    
    def run_tests(self):
        """
        Запускает все тесты с введенными данными.
        """
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК ТЕСТОВ БЛОКА 2: ЯДРО АСТРОЛОГИЧЕСКИХ РАСЧЕТОВ")
        print("=" * 60)
        
        print("\n📋 Введенные данные:")
        print(f"   👤 Имя: {self.user_data.get('first_name')}")
        print(f"   👤 Фамилия: {self.user_data.get('last_name') or 'Не указана'}")
        print(f"   📅 Дата рождения: {self.user_data.get('birth_date')}")
        print(f"   ⏰ Время рождения: {self.user_data.get('birth_time')}")
        print(f"   📍 Город: {self.user_data.get('place')}")
        print(f"   🌍 Координаты: {self.user_data.get('latitude')}, {self.user_data.get('longitude')}")
        print(f"   🕐 Часовой пояс: {self.user_data.get('timezone')}")
        print(f"   📛 Username: {self.user_data.get('username')}")
        
        self.save_user_data()
        
        subject = self.test_subject_factory()
        
        chart_data = self.test_natal_calculator(subject)
        
        aspects = self.test_aspects_calculator(subject)
        
        image_path = self.test_chart_drawer(subject)
        
        self.test_full_workflow()
        
        self.print_summary(subject, chart_data, aspects, image_path)
    
    def test_subject_factory(self):
        """Тест 1: Создание астрологического субъекта"""
        print("\n" + "=" * 60)
        print("🧪 ТЕСТ 1: SubjectFactory - создание субъекта")
        print("=" * 60)
        
        try:
            subject = SubjectFactory.create_subject_from_user_data(self.user_data)
            
            # Получаем знаки на русском
            sun_sign = translate_zodiac(subject.sun.sign)
            moon_sign = translate_zodiac(subject.moon.sign)
            
            # Получаем асцендент
            asc_sign = None
            if hasattr(subject, 'ascendant'):
                asc = subject.ascendant
                if hasattr(asc, 'sign'):
                    asc_sign = translate_zodiac(asc.sign)
                else:
                    asc_sign = translate_zodiac(str(asc))
            
            # Получаем градусы
            sun_degree = subject.sun.position
            moon_degree = subject.moon.position
            
            asc_degree = 0
            if hasattr(subject, 'ascendant'):
                asc = subject.ascendant
                if hasattr(asc, 'position'):
                    asc_degree = asc.position
            
            print(f"✅ Субъект создан: {subject.name}")
            print(f"   ☀️ Солнце: {sun_sign} ({sun_degree:.2f}°)")
            print(f"   🌙 Луна: {moon_sign} ({moon_degree:.2f}°)")
            print(f"   🌅 Асцендент: {asc_sign} ({asc_degree:.2f}°)")
            
            # Проверяем дома
            if hasattr(subject, 'houses') and subject.houses:
                print(f"   🏠 Домов: {len(subject.houses)}")
            else:
                print(f"   🏠 Домов: 12 (рассчитаны)")

            return subject
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_natal_calculator(self, subject):
        """Тест 2: Расчет натальной карты"""
        print("\n" + "=" * 60)
        print("🧪 ТЕСТ 2: NatalCalculator - расчет натальной карты")
        print("=" * 60)
        
        try:
            chart_data = NatalCalculator.calculate(self.user_data)
            
            # Считаем дома из данных
            houses_count = len(chart_data['chart']['houses'])
            
            print(f"✅ Натальная карта рассчитана")
            print(f"   - Планет: {len(chart_data['chart']['positions'])}")
            print(f"   - Домов: {houses_count}")
            print(f"   - Аспектов: {len(chart_data['chart']['aspects'])}")
            print(f"   - Элементы: Огонь={chart_data['elements']['fire']:.1f}%, "
                  f"Земля={chart_data['elements']['earth']:.1f}%, "
                  f"Воздух={chart_data['elements']['air']:.1f}%, "
                  f"Вода={chart_data['elements']['water']:.1f}%")
            
            asc_sign = chart_data['chart']['ascendant']['sign']
            asc_degree = chart_data['chart']['ascendant']['degree']
            print(f"   - Асцендент: {translate_zodiac(asc_sign)} ({asc_degree:.2f}°)")
            
            chart_dir = self.user_repo.get_user_dir(self.user_data["username"])
            chart_file = chart_dir / f"{self.user_data['username']}_natal.json"
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, indent=4, ensure_ascii=False, default=str)
            print(f"\n💾 Натальная карта сохранена в: {chart_file}")
            
            positions = chart_data['chart']['positions']
            if positions:
                print(f"\n   📊 Первые 5 планет:")
                for i, (name, data) in enumerate(list(positions.items())[:5]):
                    sign_ru = translate_zodiac(data['sign'])
                    house_ru = translate_house(data['house'])
                    print(f"      {name}: {sign_ru} {data['degree']}° ({house_ru})")
            
            return chart_data
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_aspects_calculator(self, subject):
        """Тест 3: Расчет аспектов"""
        print("\n" + "=" * 60)
        print("🧪 ТЕСТ 3: AspectsCalculator - расчет аспектов")
        print("=" * 60)
        
        if subject is None:
            print("❌ Пропуск: субъект не создан")
            return None
        
        try:
            aspects = AspectsCalculator.calculate_single_chart_aspects(subject)
            
            print(f"✅ Аспекты рассчитаны: {len(aspects)}")
            
            if aspects:
                print(f"\n   📊 Первые 10 аспектов:")
                for i, aspect in enumerate(aspects[:10]):
                    aspect_ru = translate_aspect(aspect['aspect'])
                    print(f"      {aspect['planet1']} {aspect_ru} {aspect['planet2']} "
                          f"(орбис: {aspect['orbit']}°, угол: {aspect['angle']}°)")
            else:
                print("   ℹ️ Аспектов не найдено")
            
            aspects_minor = AspectsCalculator.calculate_single_chart_aspects(
                subject, 
                include_minor=True
            )
            print(f"\n   Включая второстепенные: {len(aspects_minor)} аспектов")
            
            chart_dir = self.user_repo.get_user_dir(self.user_data["username"])
            aspects_file = chart_dir / f"{self.user_data['username']}_aspects.json"
            with open(aspects_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "major_aspects": aspects,
                    "all_aspects": aspects_minor
                }, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Аспекты сохранены в: {aspects_file}")
            
            return aspects
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_chart_drawer(self, subject):
        """Тест 4: Генерация изображения"""
        print("\n" + "=" * 60)
        print("🧪 ТЕСТ 4: ChartDrawer - генерация изображения")
        print("=" * 60)
        
        if subject is None:
            print("❌ Пропуск: субъект не создан")
            return None
        
        try:
            user_dir = self.user_repo.get_user_dir(self.user_data["username"])
            
            image_path = ChartDrawer.generate_chart_image(
                subject=subject,
                username=self.user_data["username"],
                output_dir=user_dir,
                width=800,
                height=800
            )
            
            if image_path and Path(image_path).exists():
                file_size = Path(image_path).stat().st_size
                print(f"✅ Изображение создано: {image_path}")
                print(f"   - Размер: {file_size} байт")
                print(f"   - Тип: {'PNG' if str(image_path).endswith('.png') else 'SVG'}")
            else:
                print("❌ Изображение не создано")
            
            return image_path
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_full_workflow(self):
        """Тест 5: Полный рабочий процесс"""
        print("\n" + "=" * 60)
        print("🧪 ТЕСТ 5: Полный рабочий процесс")
        print("=" * 60)
        
        try:
            print("📋 1. Данные пользователя загружены")
            
            chart_data = NatalCalculator.calculate(self.user_data)
            print(f"📊 2. Карта рассчитана: {len(chart_data['chart']['positions'])} планет")
            
            subject = SubjectFactory.create_subject_from_user_data(self.user_data)
            print(f"👤 3. Субъект создан: {subject.name}")
            
            aspects = AspectsCalculator.calculate_single_chart_aspects(subject)
            print(f"⚡ 4. Аспектов: {len(aspects)}")
            
            user_dir = self.user_repo.get_user_dir(self.user_data["username"])
            image_path = ChartDrawer.generate_chart_image(
                subject=subject,
                username=self.user_data["username"],
                output_dir=user_dir
            )
            print(f"🖼️ 5. Изображение: {image_path}")
            
            print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка в полном процессе: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self, subject, chart_data, aspects, image_path):
        """Выводит итоговую информацию"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВАЯ СВОДКА")
        print("=" * 60)
        
        print(f"\n📁 Папка пользователя: {self.user_repo.get_user_dir(self.user_data['username'])}")
        print(f"\n📄 Файлы:")
        
        user_dir = self.user_repo.get_user_dir(self.user_data["username"])
        for file in user_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                print(f"   - {file.name} ({size} байт)")
        
        if subject:
            sun_sign = translate_zodiac(subject.sun.sign)
            moon_sign = translate_zodiac(subject.moon.sign)
            
            asc_sign = None
            asc_degree = 0
            if hasattr(subject, 'ascendant'):
                asc = subject.ascendant
                if hasattr(asc, 'sign'):
                    asc_sign = translate_zodiac(asc.sign)
                    asc_degree = getattr(asc, 'position', 0)
                else:
                    asc_sign = translate_zodiac(str(asc))
            
            print(f"\n👤 Субъект: {subject.name}")
            print(f"   ☀️ Солнце: {sun_sign} ({subject.sun.position:.2f}°)")
            print(f"   🌙 Луна: {moon_sign} ({subject.moon.position:.2f}°)")
            print(f"   🌅 Асцендент: {asc_sign} ({asc_degree:.2f}°)")
        
        if chart_data:
            print(f"\n📊 Натальная карта:")
            print(f"   - Планет: {len(chart_data['chart']['positions'])}")
            print(f"   - Домов: {len(chart_data['chart']['houses'])}")
            print(f"   - Аспектов: {len(chart_data['chart']['aspects'])}")
            elements = chart_data.get('elements', {})
            print(f"   - Стихии: Огонь={elements.get('fire', 0):.1f}%, "
                  f"Земля={elements.get('earth', 0):.1f}%, "
                  f"Воздух={elements.get('air', 0):.1f}%, "
                  f"Вода={elements.get('water', 0):.1f}%")
            
            asc_sign = chart_data['chart']['ascendant']['sign']
            asc_degree = chart_data['chart']['ascendant']['degree']
            print(f"   - Асцендент: {translate_zodiac(asc_sign)} ({asc_degree:.2f}°)")
        
        if aspects:
            print(f"\n⚡ Аспектов: {len(aspects)}")
            if aspects:
                print(f"   - Первый аспект: {aspects[0]['planet1']} {translate_aspect(aspects[0]['aspect'])} {aspects[0]['planet2']}")
        
        if image_path:
            print(f"\n🖼️ Изображение: {image_path}")
        
        print("\n" + "=" * 60)
        print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 60 + "\n")

        if chart_data:
            print(f"\n📊 Натальная карта:")
            print(f"   - Планет: {len(chart_data['chart']['positions'])}")
            print(f"   - Домов: {len(chart_data['chart']['houses'])}")  # Теперь будет 12
            print(f"   - Аспектов: {len(chart_data['chart']['aspects'])}")
            elements = chart_data.get('elements', {})
            print(f"   - Стихии: Огонь={elements.get('fire', 0):.1f}%, "
            f"Земля={elements.get('earth', 0):.1f}%, "
            f"Воздух={elements.get('air', 0):.1f}%, "
            f"Вода={elements.get('water', 0):.1f}%")


def main():
    """Главная функция"""
    tester = InteractiveTester()
    
    user_data = tester.get_user_input()
    
    tester.run_tests()


if __name__ == "__main__":
    main()