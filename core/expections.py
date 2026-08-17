"""
Специфичные исключения для астрологических расчетов
"""


class AstrologyCoreError(Exception):
    """Базовое исключение для модуля core"""
    pass


class SubjectCreationError(AstrologyCoreError):
    """Ошибка при создании астрологического субъекта"""
    pass


class ChartCalculationError(AstrologyCoreError):
    """Ошибка при расчете карты"""
    pass


class AspectCalculationError(AstrologyCoreError):
    """Ошибка при расчете аспектов"""
    pass


class TransitCalculationError(AstrologyCoreError):
    """Ошибка при расчете транзитов"""
    pass


class SynastryCalculationError(AstrologyCoreError):
    """Ошибка при расчете синастрии"""
    pass


class ChartDrawingError(AstrologyCoreError):
    """Ошибка при генерации изображения карты"""
    pass


class EphemerisGenerationError(AstrologyCoreError):
    """Ошибка при генерации эфемерид"""
    pass