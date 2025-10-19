from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lingbot.translation.dictionary import Dictionary, str_to_dict


router = Router()

DICTIONARY_CALLBACK = "set_dictionary_"

# Request dictionary change
@router.message(Command("dict"))
async def select_dictionary(message: Message):
    keyboard = InlineKeyboardBuilder()
    for dictionary in Dictionary:
        keyboard.button(
            text=f"{dictionary.flag} {dictionary.label}",
            callback_data=f"{DICTIONARY_CALLBACK}{dictionary.label}"
        )
    content = Text(
        "Select dictionary:"
    )
    await message.answer(**content.as_kwargs(), reply_markup=keyboard.as_markup())

# Choose dictionary
@router.callback_query(F.data.startswith(f"{DICTIONARY_CALLBACK}"))
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
        content = Text(
            f"✅ Dictionary set to {dictionary.flag} {dictionary.label}"
        )
        await callback.message.answer(**content.as_kwargs())
    await callback.answer()
