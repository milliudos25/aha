import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
from aiogram.filters import Command
from mistralai import Mistral
import requests

# Настройки
BOT_TOKEN = "7204773293:AAGoXLtiJkwaXnU9_kkt3yKoKqZcOS6XUZA"
MISTRAL_API_KEY = "rc71c6xJKYWbnfUSlvxRDi0UkmjgNfWI"
MODEL = "mistral-large-latest"  # Используйте нужную модель

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Mistral(api_key=MISTRAL_API_KEY)

# Логирование
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("👋 Привет! Я бот на базе Mistral AI. Задавайте любые вопросы!")

@dp.message()
async def handle_message(message: Message):
    try:
        # Индикатор набора
        await bot.send_chat_action(message.chat.id, "typing")

        # Запрос к Mistral AI
        chat_response = client.chat.complete(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": message.text,
            }]
        )

        # Отправка ответа
        await message.reply(chat_response.choices[0].message.content, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("😔 Произошла ошибка. Попробуйте повторить запрос.")

async def main():
    # Проверка подключения к Telegram API
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Подключение к Telegram API успешно!")
        else:
            logging.error("Ошибка подключения к Telegram API.")
            return
    except Exception as e:
        logging.error(f"Ошибка подключения к Telegram API: {e}")
        return

    # Удаление webhook (если есть) и запуск бота
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
