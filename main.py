from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

from translate import Translation, TranslationSource


# Initialize bot and dispatcher
bot = Bot(token="")
dp = Dispatcher()

EXAMPLES_CALLBACK = "show_examples"
SOURCE_CALLBACK = "set_source_"


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello! Send me a word to translate 😊")

@dp.message(Command("source"))
async def select_source(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"{TranslationSource.RU_SK.flag} {TranslationSource.RU_SK.label}", callback_data=f"{SOURCE_CALLBACK}{TranslationSource.RU_SK.label}")
    keyboard.button(text=f"{TranslationSource.EN_SK.flag} {TranslationSource.EN_SK.label}", callback_data=f"{SOURCE_CALLBACK}{TranslationSource.EN_SK.label}")
    await message.answer("Select translation source:", reply_markup=keyboard.as_markup())


@dp.message(F.text & ~F.text.startswith("/"))
async def translate(message: Message, state: FSMContext):

    # Translation source
    user_data = await state.get_data()
    source_name = user_data.get("source", f"{TranslationSource.RU_SK.label}")  # default if not set

    source = None
    for src in TranslationSource:
        if source_name == src.label:
            source = src
    if not source:
        return

    translation = Translation(source)

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
    
    # Translation source
    user_data = await state.get_data()
    source_name = user_data.get("source", f"{TranslationSource.RU_SK.label}")  # default if not set

    source = None
    for src in TranslationSource:
        if source_name == src.label:
            source = src
    if not source:
        return

    translation = Translation(source)

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


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
