from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ErrorEvent
from dotenv import load_dotenv
import logging
import os

from lingbot.handlers import dictionary, help, start, translate


async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Initialize bot and dispatcher
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(
        token=f"{BOT_TOKEN}",
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        )
    )
    dp = Dispatcher()
    dp.include_routers(dictionary.router, help.router, start.router, translate.router)

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

    # Don't answer old messages
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)
