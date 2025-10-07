from lingbot.main import str_to_dict
from lingbot.translation import Dictionary


def test_correct_label():
    assert str_to_dict("UA-SK") == Dictionary.UA_SK

def test_incorrect_label():
    assert str_to_dict("UA_SK") == None

print(str_to_dict("UA-SK"))