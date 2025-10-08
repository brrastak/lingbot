from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ErrorEvent
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import asyncio
import logging
import os

# from lingbot import translation
from translation.dictionary import Dictionary, str_to_dict
from translation import translation


EXAMPLES_CALLBACK = "show_examples"
DICTIONARY_CALLBACK = "set_dictionary_"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Initialize bot and dispatcher
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=f"{BOT_TOKEN}")
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    current_dictionary = await get_dictionary(state)
    await message.answer("Hello! Send me a word to translate 😊\n"
                         f"*Current dictionary:* {current_dictionary.flag} {current_dictionary.label}"
                        , parse_mode="Markdown")

@dp.message(Command("dict"))
async def select_dictionary(message: Message):
    keyboard = InlineKeyboardBuilder()
    for dictionary in Dictionary:
        keyboard.button(
            text=f"{dictionary.flag} {dictionary.label}",
            callback_data=f"{DICTIONARY_CALLBACK}{dictionary.label}"
        )
    await message.answer("Select dictionary:", reply_markup=keyboard.as_markup())


@dp.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    current_dictionary = await get_dictionary(state)

    dictionaries = ", ".join(f"{src.flag} {src.label}" for src in Dictionary)

    help_text = (
        "🤖 *SlovakLingBot Help*\n\n"
        "Here’s what I can do:\n"
        "• `/start` – start the bot\n"
        "• `/help` – show this help message\n"
        f"• `/dict` – choose the dictionary ({dictionaries})\n\n"
        "Just send me *any word*, and I’ll translate it for you!\n"
        "If examples are available, tap the button to see them.\n\n"
        f"🌐 *Current dictionary:* {current_dictionary.flag} {current_dictionary.label}"
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
    word = message.text
    if word is None:
        return
    dictionary = await get_dictionary(state)
    translated = await translation.get(word, dictionary)

    logging.info("User %s requested translation for '%s'", message.from_user.id, word)

    keyboard = []
    if translated and translated.examples:
        keyboard.append([InlineKeyboardButton(text="Show examples", callback_data=f"{EXAMPLES_CALLBACK}")])

    # Add the button if there are examples
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None

    if translated is None:
        msg = "Sorry, something went wrong 😢"
    elif not translated.translations:
        msg = f"No translation found in {dictionary.flag} {dictionary.label}, try something else 🤔 "
    else:
        # The translated word should go first to be used later for collocations and examples
        msg = f"*{word}* - {', '.join(translated.translations)}"

    await message.answer(msg, reply_markup=reply_markup, parse_mode="Markdown")


# Request additional examples
@dp.callback_query(~F.data.startswith(f"{DICTIONARY_CALLBACK}"))
async def handle_keys(callback: CallbackQuery, state: FSMContext):

    if isinstance(callback.message, Message):
        original_message = callback.message.text
    else:
        await callback.answer()
        return

    if not original_message:
        await callback.answer()
        return

    word = original_message.split(" ")[0]
    logging.info("Requested examples for '%s'", word)

    lines = ["Sorry, something went wrong 😢"]

    dictionary = await get_dictionary(state)
    translated = await translation.get(word, dictionary)
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


# Choose dictionary
@dp.callback_query(F.data.startswith(f"{DICTIONARY_CALLBACK}"))
async def set_dictionary(callback: CallbackQuery, state: FSMContext):
    if callback.data:
        dictionary_label = callback.data.removeprefix(f"{DICTIONARY_CALLBACK}")
    else:
        return
    
    dictionary = str_to_dict(dictionary_label)
    if dictionary is None:
        return

    await state.update_data(dict=dictionary.label)

    if callback.message:
        await callback.message.answer(f"✅ Dictionary set to {dictionary.flag} {dictionary.label}")
    await callback.answer()


# Return Dictionary class according to the current state for the current user
async def get_dictionary(state: FSMContext) -> Dictionary:
    data = await state.get_data()
    dictionary_label = data.get("dict")
    if not isinstance(dictionary_label, str):
        # Show must go on?
        return Dictionary.default()
    
    dictionary = str_to_dict(dictionary_label)
    if not (dictionary is None):
        return dictionary
    
    return Dictionary.default()



async def main():
    await dp.start_polling(bot)

asyncio.run(main())
