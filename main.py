import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_TELEGRAM_ID
from bot_handlers import register_handlers
from webapp import router as webapp_router
import logging

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
register_handlers(dp)

@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://ваш-домен.onrender.com/webhook"  # замените после деплоя
    await bot.set_webhook(webhook_url)

@app.post("/webhook")
async def telegram_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.process_update(telegram_update)
    return {"ok": True}

app.include_router(webapp_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
