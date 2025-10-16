from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold

from translation.dictionary import Dictionary
from .utils import get_dictionary


router = Router()

@router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    current_dictionary = await get_dictionary(state)

    dictionaries = ", ".join(f"{src.flag} {src.label}" for src in Dictionary)

    help_text = Text(
        "🤖 ",
        Bold("SlovakLingBot Help\n\n"),
        "Here’s what I can do:\n"
        "• `/start` – start the bot\n"
        "• `/help` – show this help message\n"
        f"• `/dict` – choose the dictionary ({dictionaries})\n\n"
        "Just send me ",
        Bold("any word"),
        " and I’ll translate it for you!\n"
        "If examples are available, tap the button to see them.\n\n"
        "🌐 ",
        Bold("Current dictionary:"), 
        f" {current_dictionary.flag} {current_dictionary.label}"
    )

    await message.answer(**help_text.as_kwargs())
