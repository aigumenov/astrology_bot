"""
Модуль для генерации изображений натальных карт (SVG/PNG)
"""
import logging
import sys
import os
import shutil
from pathlib import Path
from io import StringIO
from typing import Optional, Dict, Any

from kerykeion import KerykeionChartSVG

from core.exceptions import ChartDrawingError

logger = logging.getLogger(__name__)


class ChartDrawer:
    """
    Генератор изображений астрологических карт.
    """
    
    DEFAULT_THEME = {
        "background_color": "#1a1a2e",
        "text_color": "#ffffff",
        "primary_color": "#e94560",
        "secondary_color": "#533483",
        "wheel_color": "#16213e"
    }
    
    @classmethod
    def generate_chart_image(
        cls,
        subject,
        username: str,
        output_dir: Path,
        theme: Optional[Dict[str, str]] = None,
        width: int = 1000,
        height: int = 1000
    ) -> Optional[Path]:
        """
        Генерирует изображение натальной карты (SVG + PNG).
        
        Args:
            subject: AstrologicalSubject
            username: Имя пользователя для имени файла
            output_dir: Папка для сохранения
            theme: Настройки цветовой схемы
            width, height: Размеры PNG-изображения
            
        Returns:
            Optional[Path]: Путь к PNG-файлу (или SVG, если PNG не создан)
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename_svg = output_dir / f"{username}_chart.svg"
            filename_png = output_dir / f"{username}_chart.png"
            
            # Используем переданную тему или тему по умолчанию
            theme = theme or cls.DEFAULT_THEME
            
            # Создаем объект для отрисовки
            chart = KerykeionChartSVG(subject)
            
            # Подавляем вывод makeSVG
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                chart.makeSVG(
                    background_color=theme["background_color"],
                    text_color=theme["text_color"],
                    primary_color=theme["primary_color"],
                    secondary_color=theme["secondary_color"],
                    wheel_color=theme["wheel_color"]
                )
            except TypeError:
                # Если параметры не поддерживаются
                chart.makeSVG()
            
            sys.stdout = old_stdout
            
            # Ищем созданный SVG файл
            svg_saved = cls._find_and_move_svg(subject.name, filename_svg)
            
            if not svg_saved:
                # Пробуем альтернативные методы сохранения
                svg_saved = cls._save_svg_alternative(chart, filename_svg)
            
            if not svg_saved:
                raise ChartDrawingError("Не удалось сохранить SVG-файл")
            
            # Конвертируем в PNG
            png_path = cls._convert_to_png(filename_svg, filename_png, width, height)
            
            if png_path and png_path.exists():
                return png_path
            
            return filename_svg if filename_svg.exists() else None
            
        except Exception as e:
            logger.error(f"Ошибка генерации изображения: {e}")
            raise ChartDrawingError(f"Не удалось сгенерировать изображение: {e}")
    
    @classmethod
    def _find_and_move_svg(cls, subject_name: str, target_path: Path) -> bool:
        """Находит SVG файл и перемещает в нужное место."""
        # Возможные имена файлов
        possible_names = [
            f"{subject_name} - Natal Chart.svg",
            f"{subject_name} Natal Chart.svg",
            f"{subject_name}-Natal-Chart.svg",
            f"{subject_name}_natal_chart.svg",
        ]
        
        # Ищем в домашней папке и текущей директории
        search_dirs = [Path.home(), Path.cwd()]
        
        for search_dir in search_dirs:
            for name in possible_names:
                file_path = search_dir / name
                if file_path.exists():
                    # Перемещаем в целевую папку
                    shutil.move(str(file_path), str(target_path))
                    logger.info(f"SVG перемещен из {file_path} в {target_path}")
                    return True
        
        # Ищем по маске
        for search_dir in search_dirs:
            matches = list(search_dir.glob("*Natal Chart*.svg"))
            if matches:
                shutil.move(str(matches[0]), str(target_path))
                logger.info(f"SVG перемещен из {matches[0]} в {target_path}")
                return True
        
        return False
    
    @classmethod
    def _save_svg_alternative(cls, chart, target_path: Path) -> bool:
        """Пробует альтернативные методы сохранения SVG."""
        try:
            # Способ 1: save_svg
            if hasattr(chart, 'save_svg'):
                chart.save_svg(str(target_path))
                return True
        except Exception:
            pass
        
        try:
            # Способ 2: saveSVG
            if hasattr(chart, 'saveSVG'):
                chart.saveSVG(str(target_path))
                return True
        except Exception:
            pass
        
        try:
            # Способ 3: Получаем контент и сохраняем вручную
            svg_content = None
            if hasattr(chart, 'get_svg'):
                svg_content = chart.get_svg()
            elif hasattr(chart, 'svg'):
                svg_content = chart.svg
            elif hasattr(chart, '_svg'):
                svg_content = chart._svg
            
            if svg_content:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                return True
        except Exception:
            pass
        
        return False
    
    @classmethod
    def _convert_to_png(
        cls,
        svg_path: Path,
        png_path: Path,
        width: int,
        height: int
    ) -> Optional[Path]:
        """
        Конвертирует SVG в PNG используя cairosvg.
        """
        if not svg_path.exists():
            logger.warning(f"SVG файл не найден: {svg_path}")
            return None
            
        try:
            import cairosvg
            
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(png_path),
                output_width=width,
                output_height=height,
                background_color="#1a1a2e"
            )
            
            logger.info(f"PNG сохранен: {png_path}")
            return png_path
            
        except ImportError:
            logger.warning("cairosvg не установлен, PNG не создан")
            return None
        except Exception as e:
            logger.warning(f"Ошибка конвертации в PNG: {e}")
            return None