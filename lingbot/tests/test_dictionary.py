from lingbot.translation.dictionary import Dictionary, str_to_dict


def test_correct_label():
    assert str_to_dict("UA-SK") == Dictionary.UA_SK

def test_incorrect_label():
    assert str_to_dict("UA_SK") is None
