from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from lingbot.translation import translation
from lingbot.handlers.utils import get_dictionary, into_markdown_messages

router = Router()

EXAMPLES_CALLBACK = "show_examples"

# Translate given word
@router.message(F.text & ~F.text.startswith("/"))
async def translate(message: Message, state: FSMContext):
    word = message.text
    if word is None:
        return
    
    logging.info("User %s requested translation for '%s'", message.from_user.id, word)

    dictionary = await get_dictionary(state)
    translated = await translation.get(word, dictionary)

    keyboard = InlineKeyboardBuilder()
    # Add the button if there are examples
    if translated and translated.examples:
        keyboard.button(
            text="Show examples",
            callback_data=f"{EXAMPLES_CALLBACK}"
        )

    if translated is None:
        content = Text("Sorry, something went wrong 😢")
    elif not translated.translations:
        content = Text(f"No translation found in {dictionary.flag} {dictionary.label}, try something else 🤔 ")
    else:
        # The translated word should go first to be used later for examples
        content = Text(
            Bold(f"{word}"),
            f" - {", ".join(translated.translations)}"
        )
    await message.answer(**content.as_kwargs(), reply_markup=keyboard.as_markup())

# Request additional examples
@router.callback_query(F.data.startswith(f"{EXAMPLES_CALLBACK}"))
async def example(callback: CallbackQuery, state: FSMContext):

    if isinstance(callback.message, Message):
        original_message = callback.message.text
    else:
        return

    if not original_message:
        return

    # Get the translated word from the previous message
    word = original_message.split(" ")[0]
    logging.info("Requested examples for '%s'", word)

    dictionary = await get_dictionary(state)
    translated = await translation.get(word, dictionary)
    if translated is None:
        messages = ["Sorry, something went wrong 😢"]
    elif not translated.examples:
        messages = ["No examples found 😢"]
    else:
        texts = [Text(
                Bold(f"{src}"),
                f" - {dst}" 
            ) for src, dst in translated.examples
        ]
        messages = into_markdown_messages(texts)

    for message in messages:
        await callback.message.answer(message)

    # Request successfully completed
    await callback.answer()
