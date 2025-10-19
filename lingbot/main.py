from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, Message, ErrorEvent
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
import asyncio
import logging
import os

from lingbot.handlers import dictionary, help, start, translate


async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Config
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    USE_POLLING = os.getenv("USE_POLLING", "false").lower() == "true"
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

    # Initialize bot and dispatcher
    bot = Bot(
        token=f"{BOT_TOKEN}",
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        )
    )
    dp = Dispatcher()
    dp.include_routers(dictionary.router, help.router, start.router, translate.router)

    # Global error handler
    @dp.errors()
    async def global_error_handler(event: ErrorEvent):
        logging.exception("Exception while handling update: %s", event.update, exc_info=event.exception)
        try:
            if event.update.message:
                await event.update.message.answer("Sorry, something went wrong 😢")
            elif event.update.callback_query:
                if isinstance(event.update.callback_query.message, Message):
                    await event.update.callback_query.message.answer("Sorry, something went wrong 😢")
        except Exception as notify_err:
            logging.warning("Couldn't send error message to user: %s", notify_err)

    async def on_startup_webhook(app: web.Application):
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook set to: {WEBHOOK_URL}")

    async def on_shutdown_webhook(app: web.Application):
        await bot.delete_webhook()
        await bot.session.close()
        logging.info("Webhook removed and session closed.")

    async def run_webhook():
        logging.info("Starting bot in WEBHOOK mode...")

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        app.on_startup.append(on_startup_webhook)
        app.on_shutdown.append(on_shutdown_webhook)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
        await site.start()

        await asyncio.Event().wait()  # keep running

    async def run_polling():
        logging.info("Starting bot in POLLING mode...")
        await dp.start_polling(bot)

    commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="help", description="Read help"),
        BotCommand(command="dict", description="Choose dictionary"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

    # Don't answer old messages
    await bot.delete_webhook(drop_pending_updates=True)
    
    if USE_POLLING:
        await run_polling()
    else:
        await run_webhook()
