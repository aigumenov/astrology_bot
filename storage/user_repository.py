"""
Модуль для работы с данными пользователей в файловой системе
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Репозиторий для управления данными пользователей.
    Все данные хранятся в папке user_data/{username}/
    """
    
    def __init__(self, base_dir: str = "data/user_data"):
        """
        Инициализация репозитория.
        
        Args:
            base_dir: Базовая директория для хранения данных пользователей
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"UserRepository инициализирован. Базовая директория: {self.base_dir}")
    
    def get_user_dir(self, username: str) -> Path:
        """
        Возвращает путь к папке пользователя, создает если не существует.
        
        Args:
            username: Уникальное имя пользователя (логин)
            
        Returns:
            Path: Путь к папке пользователя
        """
        user_dir = self.base_dir / username.lower()
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def save_user_data(self, username: str, user_data: Dict[str, Any]) -> str:
        """
        Сохраняет данные пользователя в файл {username}.json.
        
        Args:
            username: Уникальное имя пользователя
            user_data: Словарь с данными пользователя
            
        Returns:
            str: Путь к сохраненному файлу
        """
        user_dir = self.get_user_dir(username)
        filename = user_dir / f"{username}.json"
        
        # Добавляем метаданные
        user_data['_metadata'] = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=4, ensure_ascii=False, default=str)
        
        logger.info(f"Данные пользователя {username} сохранены в {filename}")
        return str(filename)
    
    def load_user_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Загружает данные пользователя из файла.
        
        Args:
            username: Уникальное имя пользователя
            
        Returns:
            Optional[Dict]: Данные пользователя или None, если файл не найден
        """
        user_dir = self.get_user_dir(username)
        filename = user_dir / f"{username}.json"
        
        if not filename.exists():
            logger.warning(f"Файл данных пользователя {username} не найден")
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Данные пользователя {username} загружены из {filename}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON для пользователя {username}: {e}")
            return None
    
    def update_user_data(self, username: str, new_data: Dict[str, Any]) -> bool:
        """
        Обновляет данные пользователя.
        
        Args:
            username: Уникальное имя пользователя
            new_data: Новые данные для обновления
            
        Returns:
            bool: True если успешно, иначе False
        """
        existing_data = self.load_user_data(username)
        if existing_data is None:
            # Если данных нет, создаем новые
            self.save_user_data(username, new_data)
            return True
        
        # Обновляем существующие данные (кроме метаданных)
        metadata = existing_data.get('_metadata', {})
        existing_data.update(new_data)
        existing_data['_metadata'] = metadata
        existing_data['_metadata']['updated_at'] = datetime.now().isoformat()
        
        self.save_user_data(username, existing_data)
        return True
    
    def user_exists(self, username: str) -> bool:
        """
        Проверяет, существует ли пользователь.
        
        Args:
            username: Уникальное имя пользователя
            
        Returns:
            bool: True если пользователь существует, иначе False
        """
        user_dir = self.get_user_dir(username)
        filename = user_dir / f"{username}.json"
        return filename.exists()
    
    def generate_username(self, first_name: str, last_name: Optional[str] = None) -> str:
        """
        Генерирует уникальное имя пользователя на основе имени и фамилии.
        
        Args:
            first_name: Имя пользователя
            last_name: Фамилия пользователя (опционально)
            
        Returns:
            str: Уникальное имя пользователя
        """
        import re
        
        # Очищаем от специальных символов
        first_clean = re.sub(r'[^a-zA-Zа-яА-Я]', '', first_name.strip().lower())
        last_clean = re.sub(r'[^a-zA-Zа-яА-Я]', '', last_name.strip().lower()) if last_name else ''
        
        # Генерируем базовое имя
        if last_clean:
            base_username = f"{first_clean}_{last_clean}"
        else:
            base_username = first_clean
        
        # Проверяем уникальность
        if not self.user_exists(base_username):
            return base_username
        
        # Если уже существует, добавляем суффикс
        counter = 1
        while True:
            username = f"{base_username}_{counter}"
            if not self.user_exists(username):
                return username
            counter += 1
    
    def get_user_files_list(self, username: str) -> list:
        """
        Возвращает список всех файлов пользователя.
        
        Args:
            username: Уникальное имя пользователя
            
        Returns:
            list: Список файлов в папке пользователя
        """
        user_dir = self.get_user_dir(username)
        return [str(f) for f in user_dir.iterdir() if f.is_file()]