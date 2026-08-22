#!/usr/bin/env python3
"""
Единый CLI-интерфейс для всех астрологических модулей

Использование:
    python cli.py --help
    python cli.py natal --username drulya
    python cli.py transits --username drulya --days 7
    python cli.py synastry --user1 drulya --user2 andrey_igumenov
    python cli.py solar --username drulya --year 2027
    python cli.py lunar --username drulya
    python cli.py ephemeris --start 2026-08-22 --end 2026-08-29
    python cli.py chart --username drulya
    python cli.py report --username drulya --save

Пример:
    python cli.py natal --username drulya --save
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from storage import UserRepository
from core import (
    SubjectFactory,
    NatalCalculator,
    AspectsCalculator,
    ChartDrawer,
    TransitsCalculator,
    ReturnsCalculator,
    EphemerisGenerator,
    SynastryCalculator
)


class AstrologyCLI:
    """
    Единый CLI-интерфейс для всех астрологических модулей.
    """
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.colors = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'red': '\033[91m',
            'purple': '\033[95m',
            'reset': '\033[0m'
        }
    
    def print_header(self, title: str):
        """Печатает заголовок."""
        print("\n" + "=" * 60)
        print(f"🧙 {title}")
        print("=" * 60)
    
    def print_success(self, message: str):
        """Печатает сообщение об успехе."""
        print(f"{self.colors['green']}✅ {message}{self.colors['reset']}")
    
    def print_info(self, message: str):
        """Печатает информационное сообщение."""
        print(f"{self.colors['blue']}ℹ️ {message}{self.colors['reset']}")
    
    def print_warning(self, message: str):
        """Печатает предупреждение."""
        print(f"{self.colors['yellow']}⚠️ {message}{self.colors['reset']}")
    
    def print_error(self, message: str):
        """Печатает сообщение об ошибке."""
        print(f"{self.colors['red']}❌ {message}{self.colors['reset']}")
    
    def print_json(self, data: Dict[str, Any], max_items: int = 5):
        """Печатает данные в удобочитаемом формате."""
        if isinstance(data, dict):
            for key, value in list(data.items())[:max_items]:
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for sub_key, sub_value in list(value.items())[:max_items]:
                        print(f"      {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    print(f"   {key}: {len(value)} элементов")
                    for i, item in enumerate(value[:max_items]):
                        if isinstance(item, dict):
                            print(f"      {i+1}. {item.get('date', item.get('name', ''))}")
                        else:
                            print(f"      {i+1}. {item}")
                else:
                    print(f"   {key}: {value}")
            if len(data) > max_items:
                print(f"   ... и еще {len(data) - max_items} полей")
    
    # ==================== МОДУЛЬ 1: Onboarding ====================
    
    def cmd_onboarding(self, args):
        """Сбор данных пользователя."""
        self.print_header("СБОР ДАННЫХ ПОЛЬЗОВАТЕЛЯ")
        
        print("\nВведите данные пользователя:")
        first_name = input("👤 Имя: ").strip()
        if not first_name:
            self.print_error("Имя обязательно")
            return
        
        last_name = input("👤 Фамилия (опционально, Enter для пропуска): ").strip()
        birth_date = input("📅 Дата рождения (ДД-ММ-ГГГГ): ").strip()
        birth_time = input("⏰ Время рождения (ЧЧ-ММ): ").strip()
        place = input("📍 Город: ").strip()
        
        # Координаты (опционально)
        print("\n🌍 Координаты (Enter для пропуска, будут использованы значения по умолчанию)")
        lat_input = input("   Широта (например, 47.2357): ").strip()
        lng_input = input("   Долгота (например, 39.7015): ").strip()
        
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "place": place,
            "latitude": float(lat_input) if lat_input else 47.2357,
            "longitude": float(lng_input) if lng_input else 39.7015,
            "timezone": "Europe/Moscow"
        }
        
        # Генерируем username
        username = self.user_repo.generate_username(first_name, last_name)
        user_data["username"] = username
        
        # Сохраняем
        self.user_repo.save_user_data(username, user_data)
        
        self.print_success(f"Пользователь {username} создан!")
        print(f"\n📁 Папка: data/user_data/{username}/")
        print(f"📄 Файл: {username}.json")
        
        return user_data
    
    # ==================== МОДУЛЬ 2: Натальная карта ====================
    
    def cmd_natal(self, args):
        """Расчет натальной карты."""
        self.print_header("РАСЧЕТ НАТАЛЬНОЙ КАРТЫ")
        
        user_data = self._load_user(args.username)
        if not user_data:
            return
        
        try:
            self.print_info(f"Расчет карты для {user_data.get('first_name')}...")
            
            # Создаем субъект
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # Рассчитываем карту
            chart_data = NatalCalculator.calculate(user_data)
            
            # Сохраняем если нужно
            if args.save:
                user_dir = self.user_repo.get_user_dir(args.username)
                chart_file = user_dir / f"{args.username}_natal.json"
                with open(chart_file, 'w', encoding='utf-8') as f:
                    json.dump(chart_data, f, indent=4, ensure_ascii=False, default=str)
                self.print_success(f"Карта сохранена: {chart_file}")
            
            # Вывод результата
            print(f"\n📊 Натальная карта для {user_data.get('first_name')}")
            print(f"   - Планет: {len(chart_data['chart']['positions'])}")
            print(f"   - Домов: {len(chart_data['chart']['houses'])}")
            print(f"   - Аспектов: {len(chart_data['chart']['aspects'])}")
            
            asc = chart_data['chart']['ascendant']
            print(f"   - Асцендент: {asc['sign']} ({asc['degree']}°)")
            
            print(f"\n   📊 Первые 5 планет:")
            positions = chart_data['chart']['positions']
            for i, (name, data) in enumerate(list(positions.items())[:5]):
                print(f"      {name}: {data['sign']} {data['degree']}° (дом {data['house']})")
            
            return chart_data
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 3: Транзиты ====================
    
    def cmd_transits(self, args):
        """Расчет транзитов."""
        self.print_header("РАСЧЕТ ТРАНЗИТОВ")
        
        user_data = self._load_user(args.username)
        if not user_data:
            return
        
        try:
            if args.days and args.days > 1:
                # Период транзитов
                start_date = datetime.now()
                end_date = start_date + timedelta(days=args.days)
                
                self.print_info(f"Расчет транзитов за {args.days} дней...")
                
                transits = TransitsCalculator.calculate_transits_period(
                    user_data=user_data,
                    start_date=start_date,
                    end_date=end_date,
                    step_days=1,
                    min_significance=args.significance or 2
                )
                
                print(f"\n📊 Транзиты за период")
                print(f"   - Период: {transits['period']['start_date'][:10]} - {transits['period']['end_date'][:10]}")
                print(f"   - Всего дней: {transits['period']['total_days']}")
                print(f"   - Дней с транзитами: {transits['statistics']['days_with_aspects']}")
                print(f"   - Среднее аспектов в день: {transits['statistics']['avg_aspects_per_day']}")
                
                if transits['significant_days']:
                    print(f"\n   📊 Самые значимые дни:")
                    for i, day in enumerate(transits['significant_days'][:3]):
                        print(f"      {i+1}. {day['date']} — {day['aspects_count']} аспектов")
                
                if args.save:
                    user_dir = self.user_repo.get_user_dir(args.username)
                    file_path = TransitsCalculator.save_transits_to_file(
                        transits_data=transits,
                        username=args.username,
                        output_dir=user_dir,
                        filename=f"{args.username}_transits_period_{args.days}d.json"
                    )
                    self.print_success(f"Транзиты сохранены: {file_path}")
                
                return transits
            else:
                # Текущие транзиты
                self.print_info("Расчет текущих транзитов...")
                
                transits = TransitsCalculator.calculate_current_transits(
                    user_data=user_data,
                    min_significance=args.significance or 2
                )
                
                print(f"\n📊 Текущие транзиты")
                print(f"   - Дата: {transits['transit_date'][:19]}")
                print(f"   - Всего аспектов: {transits['aspects']['total_all']}")
                print(f"   - Значимых аспектов: {transits['aspects']['total']}")
                print(f"   - Оценка дня: {transits['day_score']['overall']} ({transits['day_score']['level']})")
                print(f"   - Сводка: {transits['summary']}")
                
                if transits['aspects']['list']:
                    print(f"\n   📊 Значимые аспекты:")
                    for i, aspect in enumerate(transits['aspects']['list'][:5]):
                        print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)")
                
                if args.save:
                    user_dir = self.user_repo.get_user_dir(args.username)
                    file_path = TransitsCalculator.save_transits_to_file(
                        transits_data=transits,
                        username=args.username,
                        output_dir=user_dir,
                        filename=f"{args.username}_transits_current.json"
                    )
                    self.print_success(f"Транзиты сохранены: {file_path}")
                
                return transits
                
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 4: Синастрия ====================
    
    def cmd_synastry(self, args):
        """Расчет синастрии (совместимости)."""
        self.print_header("РАСЧЕТ СИНАСТРИИ")
        
        user1_data = self._load_user(args.user1)
        if not user1_data:
            return
        
        user2_data = self._load_user(args.user2)
        if not user2_data:
            return
        
        try:
            self.print_info(f"Расчет совместимости между {args.user1} и {args.user2}...")
            
            synastry = SynastryCalculator.calculate_synastry(
                user1_data=user1_data,
                user2_data=user2_data,
                include_minor_aspects=args.minor,
                min_significance=args.significance or 2
            )
            
            print(f"\n📊 Совместимость: {args.user1} и {args.user2}")
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
            
            if args.report:
                print(f"\n📄 ОТЧЕТ О СОВМЕСТИМОСТИ:")
                print(synastry['report'])
            
            if args.save:
                user_dir = self.user_repo.get_user_dir("synastry")
                file_path = SynastryCalculator.save_synastry_to_file(
                    synastry_data=synastry,
                    username1=args.user1,
                    username2=args.user2,
                    output_dir=user_dir
                )
                self.print_success(f"Синастрия сохранена: {file_path}")
            
            return synastry
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 5: Солярное возвращение ====================
    
    def cmd_solar(self, args):
        """Расчет солярного возвращения."""
        self.print_header("СОЛЯРНОЕ ВОЗВРАЩЕНИЕ")
        
        user_data = self._load_user(args.username)
        if not user_data:
            return
        
        try:
            year = args.year or datetime.now().year + 1
            
            self.print_info(f"Расчет солярного возвращения на {year} год...")
            
            solar = ReturnsCalculator.calculate_solar_return(
                user_data=user_data,
                year=year,
                city=args.city or user_data.get('place', 'Current Location')
            )
            
            print(f"\n📊 Солярное возвращение на {year} год")
            print(f"   - Дата: {solar['return_date']}")
            print(f"   - Асцендент: {solar['ascendant']['sign']} ({solar['ascendant']['degree']}°)")
            print(f"   - Всего аспектов: {solar['aspects']['total']}")
            print(f"   - Сводка: {solar['summary']}")
            
            if solar['aspects']['list']:
                print(f"\n   📊 Первые 5 аспектов:")
                for i, aspect in enumerate(solar['aspects']['list'][:5]):
                    print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)")
            
            if args.save:
                user_dir = self.user_repo.get_user_dir(args.username)
                file_path = ReturnsCalculator.save_return_to_file(
                    return_data=solar,
                    username=args.username,
                    output_dir=user_dir
                )
                self.print_success(f"Солярное возвращение сохранено: {file_path}")
            
            return solar
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 6: Лунное возвращение ====================
    
    def cmd_lunar(self, args):
        """Расчет лунного возвращения."""
        self.print_header("ЛУННОЕ ВОЗВРАЩЕНИЕ")
        
        user_data = self._load_user(args.username)
        if not user_data:
            return
        
        try:
            self.print_info("Расчет следующего лунного возвращения...")
            
            lunar = ReturnsCalculator.calculate_next_lunar_return(
                user_data=user_data,
                city=args.city or user_data.get('place', 'Current Location')
            )
            
            print(f"\n📊 Лунное возвращение")
            print(f"   - Дата: {lunar['return_date']}")
            print(f"   - Асцендент: {lunar['ascendant']['sign']} ({lunar['ascendant']['degree']}°)")
            print(f"   - Всего аспектов: {lunar['aspects']['total']}")
            print(f"   - Сводка: {lunar['summary']}")
            
            if lunar['aspects']['list']:
                print(f"\n   📊 Первые 5 аспектов:")
                for i, aspect in enumerate(lunar['aspects']['list'][:5]):
                    print(f"      {i+1}. {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)")
            
            if args.save:
                user_dir = self.user_repo.get_user_dir(args.username)
                file_path = ReturnsCalculator.save_return_to_file(
                    return_data=lunar,
                    username=args.username,
                    output_dir=user_dir
                )
                self.print_success(f"Лунное возвращение сохранено: {file_path}")
            
            return lunar
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 7: Эфемериды ====================
    
    def cmd_ephemeris(self, args):
        """Генерация эфемерид."""
        self.print_header("ГЕНЕРАЦИЯ ЭФЕМЕРИД")
        
        try:
            start_date = args.start or datetime.now().strftime("%Y-%m-%d")
            end_date = args.end or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            self.print_info(f"Генерация эфемерид с {start_date} по {end_date}...")
            
            ephemeris = EphemerisGenerator.generate_daily_ephemeris(
                start_date=start_date,
                end_date=end_date,
                latitude=args.latitude or 55.7558,
                longitude=args.longitude or 37.6173,
                timezone=args.timezone or "Europe/Moscow"
            )
            
            print(f"\n📊 Эфемериды")
            print(f"   - Период: {ephemeris['period']['start_date'][:10]} - {ephemeris['period']['end_date'][:10]}")
            print(f"   - Всего дней: {ephemeris['period']['total_days']}")
            print(f"   - Планет в дне: {len(ephemeris['days'][0]['planets']) if ephemeris['days'] else 0}")
            
            if ephemeris['days'] and args.verbose:
                print(f"\n   📊 Первые 3 дня:")
                for day in ephemeris['days'][:3]:
                    print(f"      {day['date'][:10]}: {len(day['planets'])} планет")
            
            if args.save:
                output_dir = Path("test_output")
                file_path = EphemerisGenerator.save_ephemeris_to_file(
                    ephemeris_data=ephemeris,
                    filename=f"ephemeris_{start_date}_{end_date}.json",
                    output_dir=output_dir
                )
                self.print_success(f"Эфемериды сохранены: {file_path}")
            
            return ephemeris
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 8: Изображение карты ====================
    
    def cmd_chart(self, args):
        """Генерация изображения натальной карты."""
        self.print_header("ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ КАРТЫ")
        
        user_data = self._load_user(args.username)
        if not user_data:
            return
        
        try:
            self.print_info(f"Генерация изображения для {user_data.get('first_name')}...")
            
            # Создаем субъект
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            
            # Генерируем изображение
            user_dir = self.user_repo.get_user_dir(args.username)
            image_path = ChartDrawer.generate_chart_image(
                subject=subject,
                username=args.username,
                output_dir=user_dir,
                width=args.width or 1000,
                height=args.height or 1000
            )
            
            if image_path and Path(image_path).exists():
                file_size = Path(image_path).stat().st_size
                self.print_success(f"Изображение создано: {image_path}")
                print(f"   - Размер: {file_size} байт")
                print(f"   - Тип: {'PNG' if str(image_path).endswith('.png') else 'SVG'}")
            else:
                self.print_error("Изображение не создано")
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== МОДУЛЬ 9: Полный отчет ====================
    
    def cmd_report(self, args):
        """Генерация полного отчета по пользователю."""
        self.print_header("ПОЛНЫЙ ОТЧЕТ")
        
        user_data = self._load_user(args.username)
        if not user_data:
            return
        
        try:
            self.print_info(f"Генерация полного отчета для {user_data.get('first_name')}...")
            
            # 1. Натальная карта
            chart_data = NatalCalculator.calculate(user_data)
            
            # 2. Аспекты
            subject = SubjectFactory.create_subject_from_user_data(user_data)
            aspects = AspectsCalculator.calculate_single_chart_aspects(subject)
            
            # 3. Текущие транзиты
            transits = TransitsCalculator.calculate_current_transits(user_data)
            
            # 4. Солярное возвращение на следующий год
            next_year = datetime.now().year + 1
            solar = ReturnsCalculator.calculate_solar_return(
                user_data=user_data,
                year=next_year,
                city=user_data.get('place', 'Current Location')
            )
            
            # Формируем отчет
            report = f"""
{'='*60}
📊 ПОЛНЫЙ АСТРОЛОГИЧЕСКИЙ ОТЧЕТ
{'='*60}

👤 Пользователь: {user_data.get('first_name')} {user_data.get('last_name', '')}
📅 Дата рождения: {user_data.get('birth_date')}
⏰ Время рождения: {user_data.get('birth_time')}
📍 Город: {user_data.get('place', '')}

{'='*60}
📊 НАТАЛЬНАЯ КАРТА
{'='*60}
   - Планет: {len(chart_data['chart']['positions'])}
   - Домов: {len(chart_data['chart']['houses'])}
   - Аспектов: {len(chart_data['chart']['aspects'])}
   - Асцендент: {chart_data['chart']['ascendant']['sign']} ({chart_data['chart']['ascendant']['degree']}°)

📊 СТИХИИ:
   - Огонь: {chart_data['elements']['fire']:.1f}%
   - Земля: {chart_data['elements']['earth']:.1f}%
   - Воздух: {chart_data['elements']['air']:.1f}%
   - Вода: {chart_data['elements']['water']:.1f}%

📊 КАЧЕСТВА:
   - Кардинальные: {chart_data['qualities']['cardinal']:.1f}%
   - Фиксированные: {chart_data['qualities']['fixed']:.1f}%
   - Мутабельные: {chart_data['qualities']['mutable']:.1f}%

{'='*60}
🌅 АСЦЕНДЕНТ И ПЛАНЕТЫ
{'='*60}
"""
            
            asc = chart_data['chart']['ascendant']
            report += f"Асцендент: {asc['sign']} ({asc['degree']}°)\n\n"
            
            report += "Планеты:\n"
            positions = chart_data['chart']['positions']
            for name, data in list(positions.items())[:10]:
                report += f"   {name}: {data['sign']} {data['degree']}° (дом {data['house']})\n"
            
            report += f"""
{'='*60}
⚡ АСПЕКТЫ ({len(aspects)})
{'='*60}
"""
            for i, aspect in enumerate(aspects[:10]):
                report += f"   {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)\n"
            
            report += f"""
{'='*60}
🔮 ТРАНЗИТЫ НА СЕГОДНЯ
{'='*60}
   - Оценка дня: {transits['day_score']['overall']} ({transits['day_score']['level']})
   - Сводка: {transits['summary']}
   - Значимых аспектов: {transits['aspects']['total']}
"""
            
            if transits['aspects']['list']:
                report += "\n   Значимые транзиты:\n"
                for aspect in transits['aspects']['list'][:5]:
                    report += f"      {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)\n"
            
            report += f"""
{'='*60}
🌞 СОЛЯРНОЕ ВОЗВРАЩЕНИЕ НА {next_year} ГОД
{'='*60}
   - Дата: {solar['return_date']}
   - Асцендент: {solar['ascendant']['sign']} ({solar['ascendant']['degree']}°)
   - Сводка: {solar['summary']}
"""
            
            if solar['aspects']['list']:
                report += "\n   Основные аспекты года:\n"
                for i, aspect in enumerate(solar['aspects']['list'][:5]):
                    report += f"      {aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (орбис: {aspect['orbit']}°)\n"
            
            report += f"""
{'='*60}
📁 Файлы пользователя
{'='*60}
   - data/user_data/{args.username}/{args.username}.json
   - data/user_data/{args.username}/{args.username}_natal.json
   - data/user_data/{args.username}/{args.username}_chart.png
"""
            
            # Сохраняем отчет
            if args.save:
                user_dir = self.user_repo.get_user_dir(args.username)
                report_file = user_dir / f"{args.username}_report.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                self.print_success(f"Отчет сохранен: {report_file}")
            
            print(report)
            
            return report
            
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== Вспомогательные методы ====================
    
    def _load_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Загружает данные пользователя."""
        user_data = self.user_repo.load_user_data(username)
        if not user_data:
            self.print_error(f"Пользователь '{username}' не найден")
            self.print_info("Доступные пользователи:")
            user_dir = Path("data/user_data")
            if user_dir.exists():
                for user_folder in user_dir.iterdir():
                    if user_folder.is_dir() and (user_folder / f"{user_folder.name}.json").exists():
                        print(f"   - {user_folder.name}")
            return None
        return user_data
    
    def _get_parser(self):
        """Создает парсер аргументов."""
        parser = argparse.ArgumentParser(
            description="Астрологический CLI-интерфейс",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры:
  python cli.py onboarding                           # Создать нового пользователя
  python cli.py natal --username drulya              # Рассчитать натальную карту
  python cli.py transits --username drulya          # Текущие транзиты
  python cli.py transits --username drulya --days 7 # Транзиты на 7 дней
  python cli.py synastry --user1 drulya --user2 andrey_igumenov --report
  python cli.py solar --username drulya --year 2027
  python cli.py lunar --username drulya
  python cli.py ephemeris --start 2026-08-22 --end 2026-08-29
  python cli.py chart --username drulya
  python cli.py report --username drulya --save
            """
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
        
        # Команда: onboarding
        subparsers.add_parser("onboarding", help="Создать нового пользователя")
        
        # Команда: natal
        natal_parser = subparsers.add_parser("natal", help="Рассчитать натальную карту")
        natal_parser.add_argument("--username", "-u", required=True, help="Имя пользователя")
        natal_parser.add_argument("--save", "-s", action="store_true", help="Сохранить результат")
        
        # Команда: transits
        transits_parser = subparsers.add_parser("transits", help="Рассчитать транзиты")
        transits_parser.add_argument("--username", "-u", required=True, help="Имя пользователя")
        transits_parser.add_argument("--days", "-d", type=int, default=1, help="Количество дней (1 для текущих)")
        transits_parser.add_argument("--significance", "-sig", type=int, default=2, help="Минимальная значимость (1-5)")
        transits_parser.add_argument("--save", "-s", action="store_true", help="Сохранить результат")
        
        # Команда: synastry
        synastry_parser = subparsers.add_parser("synastry", help="Рассчитать синастрию")
        synastry_parser.add_argument("--user1", "-u1", required=True, help="Имя первого пользователя")
        synastry_parser.add_argument("--user2", "-u2", required=True, help="Имя второго пользователя")
        synastry_parser.add_argument("--minor", "-m", action="store_true", help="Включить второстепенные аспекты")
        synastry_parser.add_argument("--significance", "-sig", type=int, default=2, help="Минимальная значимость (1-5)")
        synastry_parser.add_argument("--report", "-r", action="store_true", help="Показать текстовый отчет")
        synastry_parser.add_argument("--save", "-s", action="store_true", help="Сохранить результат")
        
        # Команда: solar
        solar_parser = subparsers.add_parser("solar", help="Рассчитать солярное возвращение")
        solar_parser.add_argument("--username", "-u", required=True, help="Имя пользователя")
        solar_parser.add_argument("--year", "-y", type=int, help="Год для расчета (по умолчанию следующий)")
        solar_parser.add_argument("--city", "-c", help="Город для возвращения")
        solar_parser.add_argument("--save", "-s", action="store_true", help="Сохранить результат")
        
        # Команда: lunar
        lunar_parser = subparsers.add_parser("lunar", help="Рассчитать лунное возвращение")
        lunar_parser.add_argument("--username", "-u", required=True, help="Имя пользователя")
        lunar_parser.add_argument("--city", "-c", help="Город для возвращения")
        lunar_parser.add_argument("--save", "-s", action="store_true", help="Сохранить результат")
        
        # Команда: ephemeris
        ephemeris_parser = subparsers.add_parser("ephemeris", help="Сгенерировать эфемериды")
        ephemeris_parser.add_argument("--start", help="Начальная дата (YYYY-MM-DD)")
        ephemeris_parser.add_argument("--end", help="Конечная дата (YYYY-MM-DD)")
        ephemeris_parser.add_argument("--latitude", "-lat", type=float, default=55.7558, help="Широта")
        ephemeris_parser.add_argument("--longitude", "-lng", type=float, default=37.6173, help="Долгота")
        ephemeris_parser.add_argument("--timezone", "-tz", default="Europe/Moscow", help="Часовой пояс")
        ephemeris_parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
        ephemeris_parser.add_argument("--save", "-s", action="store_true", help="Сохранить результат")
        
        # Команда: chart
        chart_parser = subparsers.add_parser("chart", help="Сгенерировать изображение карты")
        chart_parser.add_argument("--username", "-u", required=True, help="Имя пользователя")
        chart_parser.add_argument("--width", "-w", type=int, default=1000, help="Ширина PNG")
        chart_parser.add_argument("--height", "-ht", type=int, default=1000, help="Высота PNG")
        
        # Команда: report
        report_parser = subparsers.add_parser("report", help="Сгенерировать полный отчет")
        report_parser.add_argument("--username", "-u", required=True, help="Имя пользователя")
        report_parser.add_argument("--save", "-s", action="store_true", help="Сохранить отчет в файл")
        
        return parser
    
    def run(self, args=None):
        """Запускает CLI."""
        parser = self._get_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        # Сопоставление команд с методами
        commands = {
            "onboarding": self.cmd_onboarding,
            "natal": self.cmd_natal,
            "transits": self.cmd_transits,
            "synastry": self.cmd_synastry,
            "solar": self.cmd_solar,
            "lunar": self.cmd_lunar,
            "ephemeris": self.cmd_ephemeris,
            "chart": self.cmd_chart,
            "report": self.cmd_report,
        }
        
        if parsed_args.command in commands:
            commands[parsed_args.command](parsed_args)
        else:
            self.print_error(f"Неизвестная команда: {parsed_args.command}")
            parser.print_help()


def main():
    """Главная функция."""
    cli = AstrologyCLI()
    cli.run()


if __name__ == "__main__":
    main()