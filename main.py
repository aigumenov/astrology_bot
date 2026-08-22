#!/usr/bin/env python3
"""
Точка входа для Bothost
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем папку для данных
Path("data/user_data").mkdir(parents=True, exist_ok=True)

try:
    # Пробуем импортировать из api.py
    from api import app
    logger.info("✅ Приложение загружено из api.py")
except ImportError:
    try:
        # Пробуем импортировать из max_bot.py
        from max_bot import app
        logger.info("✅ Приложение загружено из max_bot.py")
    except ImportError:
        # Если нет ни одного, создаем минимальное приложение
        from fastapi import FastAPI
        app = FastAPI(title="Astrology Bot")
        
        @app.get("/")
        async def root():
            return {
                "status": "ok",
                "message": "Astrology Bot is running",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @app.post("/webhook")
        async def webhook(request: Request):
            try:
                data = await request.json()
                logger.info(f"Получен webhook: {data}")
                return {"status": "ok"}
            except Exception as e:
                logger.error(f"Ошибка webhook: {e}")
                return {"status": "error", "detail": str(e)}
        
        logger.info("⚠️ Создано минимальное приложение")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    logger.info(f"🚀 Запуск сервера на порту {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )