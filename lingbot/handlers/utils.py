from aiogram.fsm.context import FSMContext

from translation.dictionary import Dictionary, str_to_dict


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
