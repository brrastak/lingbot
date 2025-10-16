from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold

from .utils import get_dictionary


router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    current_dictionary = await get_dictionary(state)
    content = Text(
        "Hello! Send me a word to translate 😊\n",
        Bold("Current dictionary:"),
        f" {current_dictionary.flag} {current_dictionary.label}"
    )
    await message.answer(**content.as_kwargs())
