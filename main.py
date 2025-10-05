from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ErrorEvent
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import logging
import os

from translate import Translator, TranslationSource


EXAMPLES_CALLBACK = "show_examples"
SOURCE_CALLBACK = "set_source_"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Initialize bot and dispatcher
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=f"{BOT_TOKEN}")
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello! Send me a word to translate 😊")

@dp.message(Command("source"))
async def select_source(message: Message):
    keyboard = InlineKeyboardBuilder()
    for src in TranslationSource:
        keyboard.button(
            text=f"{src.flag} {src.label}",
            callback_data=f"{SOURCE_CALLBACK}{src.label}"
        )
    await message.answer("Select translation source:", reply_markup=keyboard.as_markup())


@dp.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    # Get user data from FSM
    data = await state.get_data()
    source_label = data.get("source")

    source = TranslationSource.RU_SK
    for src in TranslationSource:
        if source_label == src.label:
            source = src

    help_text = (
        "🤖 *LingBot Help*\n\n"
        "Here’s what I can do:\n"
        "• `/start` – start the bot\n"
        "• `/help` – show this help message\n"
        "• `/source` – choose the translation source (🇷🇺 RU–SK or 🇬🇧 EN–SK)\n\n"
        "Just send me *any word*, and I’ll translate it for you!\n"
        "If examples are available, tap the button to see them.\n\n"
        f"🌐 *Current source:* {source.flag} {source.label}"
    )

    await message.answer(help_text, parse_mode="Markdown")


@dp.errors()
async def global_error_handler(event: ErrorEvent):
    logging.exception("Exception while handling update: %s", event.update, exc_info=event.exception)
    try:
        if event.update.message:
            await event.update.message.answer("Something went wrong 😢")
        elif event.update.callback_query:
            if isinstance(event.update.callback_query.message, Message):
                await event.update.callback_query.message.answer("Something went wrong 😢")
    except Exception as notify_err:
        logging.warning("Couldn't send error message to user: %s", notify_err)


# Translate given word
@dp.message(F.text & ~F.text.startswith("/"))
async def translate(message: Message, state: FSMContext):
    translator = await get_translator(state)
    word = message.text
    translated = await translator.get(word)

    logging.info("User %s requested translation for '%s'", message.from_user.id, word)

    keyboard = []
    if translated and translated.examples:
        keyboard.append([InlineKeyboardButton(text="Show examples", callback_data=f"{EXAMPLES_CALLBACK}")])

    # Add the button if there are examples
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None

    if translated is None:
        msg = "Sorry, something went wrong 😢"
    elif not translated.translations:
        msg = "No translation found, try something else 🤔"
    else:
        # The translated word should go first to be used later for collocations and examples
        msg = f"*{word}* - {', '.join(translated.translations)}"

    await message.answer(msg, reply_markup=reply_markup, parse_mode="Markdown")


# Request additional examples
@dp.callback_query(~F.data.startswith(f"{SOURCE_CALLBACK}"))
async def handle_keys(callback: CallbackQuery, state: FSMContext):

    if isinstance(callback.message, Message):
        original_message = callback.message.text
    else:
        await callback.answer()
        return

    if not original_message:
        await callback.answer()
        return
    
    translator = await get_translator(state)

    word = original_message.split(" ")[0]
    logging.info("Requested examples for '%s'", word)

    lines = ["Sorry, something went wrong 😢"]

    translated = await translator.get(word)
    if translated is None:
        pass
    else:
        data = callback.data
        if data == f"{EXAMPLES_CALLBACK}":
            if not translated.examples:
                lines = ["No examples found 😢"]
            else:
                lines = [f"*{src}* - {dst}" for src, dst in translated.examples]

    MAX_LENGTH = 4000  # a bit smaller than 4096 for safety
    current_msg = ""

    for line in lines:
        if len(current_msg) + len(line) + 1 > MAX_LENGTH:
            await callback.message.answer(current_msg, parse_mode="Markdown")
            current_msg = ""
        current_msg += line + "\n"

    # Send the last chunk
    if current_msg:
        await callback.message.answer(current_msg, parse_mode="Markdown")

    await callback.answer()  # Always answer callback queries


# Choose translation source (RU-SK / EN-SK)
@dp.callback_query(F.data.startswith(f"{SOURCE_CALLBACK}"))
async def set_source(callback: CallbackQuery, state: FSMContext):
    if callback.data:
        source_label = callback.data.removeprefix(f"{SOURCE_CALLBACK}")
    else:
        await callback.answer()
        return
    
    await state.update_data(source=source_label)
    # await state.update_data(source=source_code)

    source_flag = ""
    for source in TranslationSource:
        if source_label == source.label:
            source_flag = source.flag
    if not source_flag:
        await callback.answer()
        return

    if callback.message:
        await callback.message.answer(f"✅ Source set to {source_label} {source_flag}")
    await callback.answer()


# Return Translation class according to the current state for the current user
async def get_translator(state: FSMContext) -> Translator:
    data = await state.get_data()
    source_label = data.get("source")

    source = TranslationSource.RU_SK
    for src in TranslationSource:
        if source_label == src.label:
            source = src
    
    return Translator(source)




async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
