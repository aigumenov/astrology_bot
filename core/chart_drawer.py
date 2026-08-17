"""
Модуль для генерации изображений натальных карт (SVG/PNG)
"""
import logging
import sys
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
            
            # Получаем SVG-контент
            svg_content = cls._get_svg_content(chart)
            
            if svg_content:
                # Сохраняем SVG
                with open(filename_svg, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                logger.info(f"SVG сохранен: {filename_svg}")
            else:
                # Пробуем найти файл, созданный makeSVG
                default_path = Path(f"{subject.name} - Natal Chart.svg")
                if default_path.exists():
                    default_path.rename(filename_svg)
                    logger.info(f"SVG перенесен в: {filename_svg}")
                else:
                    raise ChartDrawingError("Не удалось получить SVG-контент")
            
            # Конвертируем в PNG
            png_path = cls._convert_to_png(filename_svg, filename_png, width, height)
            
            if png_path:
                return png_path
            
            return filename_svg
            
        except Exception as e:
            logger.error(f"Ошибка генерации изображения: {e}")
            raise ChartDrawingError(f"Не удалось сгенерировать изображение: {e}")
    
    @classmethod
    def _get_svg_content(cls, chart) -> Optional[str]:
        """Получает SVG-контент из объекта chart."""
        if hasattr(chart, 'get_svg'):
            return chart.get_svg()
        elif hasattr(chart, 'svg'):
            return chart.svg
        elif hasattr(chart, '_svg'):
            return chart._svg
        elif hasattr(chart, 'output'):
            return chart.output
        return None
    
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