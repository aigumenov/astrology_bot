"""
Модуль валидации пользовательского ввода
"""
from datetime import datetime
from typing import Tuple, Optional
import re


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Проверяет корректность имени.
    
    Args:
        name: Имя пользователя
        
    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Имя не может быть пустым"
    
    if len(name.strip()) < 2:
        return False, "Имя должно содержать минимум 2 символа"
    
    if len(name.strip()) > 50:
        return False, "Имя не должно превышать 50 символов"
    
    # Разрешаем буквы, пробелы, дефисы и апострофы
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-\']+$', name.strip()):
        return False, "Имя может содержать только буквы, пробелы, дефис или апостроф"
    
    return True, ""


def validate_birth_date(date_str: str) -> Tuple[bool, str, Optional[datetime]]:
    """
    Проверяет корректность даты рождения в формате ДД-ММ-ГГГГ.
    
    Args:
        date_str: Дата в формате ДД-ММ-ГГГГ
        
    Returns:
        (is_valid, error_message, datetime_object)
    """
    if not date_str or not date_str.strip():
        return False, "Дата рождения обязательна для заполнения", None
    
    date_str = date_str.strip()
    
    # Проверяем формат
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
        return False, "Неверный формат! Используйте ДД-ММ-ГГГГ (например: 25-11-1986)", None
    
    try:
        birth_date = datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return False, "Неверная дата! Проверьте правильность введенных чисел", None
    
    # Проверяем, что дата не в будущем
    if birth_date > datetime.now():
        return False, "Дата рождения не может быть в будущем!", None
    
    # Проверяем, что дата не слишком старая (максимум 120 лет)
    if birth_date.year < 1900:
        return False, "Год рождения должен быть не ранее 1900", None
    
    return True, "", birth_date


def validate_birth_time(time_str: str) -> Tuple[bool, str, Optional[Tuple[int, int]]]:
    """
    Проверяет корректность времени рождения в формате ЧЧ-ММ.
    
    Args:
        time_str: Время в формате ЧЧ-ММ
        
    Returns:
        (is_valid, error_message, (hour, minute))
    """
    if not time_str or not time_str.strip():
        return False, "Время рождения обязательно для заполнения", None
    
    time_str = time_str.strip()
    
    # Проверяем формат
    if not re.match(r'^\d{2}-\d{2}$', time_str):
        return False, "Неверный формат! Используйте ЧЧ-ММ (например: 06-10)", None
    
    try:
        hour, minute = map(int, time_str.split('-'))
    except ValueError:
        return False, "Неверный формат! Используйте ЧЧ-ММ (например: 06-10)", None
    
    if not (0 <= hour <= 23):
        return False, "Часы должны быть от 0 до 23", None
    
    if not (0 <= minute <= 59):
        return False, "Минуты должны быть от 0 до 59", None
    
    return True, "", (hour, minute)


def validate_place(place: str) -> Tuple[bool, str]:
    """
    Проверяет корректность названия города.
    
    Args:
        place: Название города
        
    Returns:
        (is_valid, error_message)
    """
    if not place or not place.strip():
        return False, "Название города обязательно для заполнения"
    
    if len(place.strip()) < 2:
        return False, "Название города должно содержать минимум 2 символа"
    
    if len(place.strip()) > 100:
        return False, "Название города не должно превышать 100 символов"
    
    return True, ""