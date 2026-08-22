#!/usr/bin/env python3
"""
Точка входа для Bothost
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

# Импортируем приложение из api.py или max_bot.py
try:
    from api import app
except ImportError:
    try:
        from max_bot import app
    except ImportError:
        # Если нет ни api.py, ни max_bot.py, создаем минимальное приложение
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        async def root():
            return {"status": "ok", "message": "Astrology bot is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )