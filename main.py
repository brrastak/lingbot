from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

from translate import Translation, TranslationSource


# Initialize bot and dispatcher
bot = Bot(token="")
dp = Dispatcher()

translation = Translation(TranslationSource.RU_SK)

EXAMPLES_CALLBACK = "show_examples"


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello! Send me a word to translate 😊")


@dp.message(F.text & ~F.text.startswith("/"))
async def translate(message: Message):
    word = message.text
    translated = translation.get(word)

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
        msg = f"\"{word}\" - {', '.join(translated.translations)}"

    await message.answer(msg, reply_markup=reply_markup)


@dp.callback_query()
async def handle_keys(callback: CallbackQuery):


    if isinstance(callback.message, Message):
        original_message = callback.message.text
    else:
        await callback.answer()
        return

    if not original_message:
        await callback.answer()
        return
    
    word = original_message.split('"')[1]

    lines = ["Sorry, something went wrong 😢"]

    translated = translation.get(word)
    if translated is None:
        pass
    else:
        data = callback.data
        if data == f"{EXAMPLES_CALLBACK}":
            if not translated.examples:
                lines = ["No examples found 😢"]
            else:
                lines = [f"{src} - {dst}" for src, dst in translated.examples]
                


    MAX_LENGTH = 4000  # a bit smaller than 4096 for safety

    current_msg = ""

    for line in lines:
        if len(current_msg) + len(line) + 1 > MAX_LENGTH:
            await callback.message.answer(current_msg)
            current_msg = ""
        current_msg += line + "\n"

    # Send the last chunk
    if current_msg:
        await callback.message.answer(current_msg)

    await callback.answer()  # Always answer callback queries


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
