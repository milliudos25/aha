import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from mistralai import Mistral
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Настройки через переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "7204773293:AAGoXLtiJkwaXnU9_kkt3yKoKqZcOS6XUZA")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "rc71c6xJKYWbnfUSlvxRDi0UkmjgNfWI")
MODEL = "mistral-large-latest"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Mistral(api_key=MISTRAL_API_KEY)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


async def on_startup(bot: Bot):
    # Получаем URL текущего приложения
    WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "https://your-app-name.onrender.com") + WEBHOOK_PATH

    # Устанавливаем webhook
    await bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True
    )
    logger.info(f"Установлен webhook: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    logger.info("Отключение бота...")
    await bot.delete_webhook()


async def main():
    # Создаем приложение
    app = web.Application()

    # Настраиваем обработчик вебхука
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=BOT_TOKEN[:50]  # Используем первые 50 символов токена как secret
    )

    # Регистрируем обработчик
    webhook_handler.register(app, path=WEBHOOK_PATH)

    # Регистрируем хендлеры запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Настраиваем маршрут для проверки работоспособности
    async def health_check(request):
        return web.Response(text="Bot is running")

    app.router.add_get("/", health_check)

    # Запускаем приложение
    return app


if __name__ == "__main__":
    app = asyncio.run(main())
    web.run_app(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT)