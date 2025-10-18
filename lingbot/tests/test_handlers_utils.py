from aiogram.utils.formatting import Text, Bold

from lingbot.handlers.utils import into_markdown_messages


def test_short_message():
    expexted = ["*Short* message\n"]

    text = Text(
        Bold("Short"),
        " message"
    )
    actual = into_markdown_messages([text])

    assert actual == expexted

def test_long_message():
    MAX_LEN = 4096
    ITEM_NUM = MAX_LEN // 32 + 1
    text = Text(
        Bold("Text"),
        " with expected len -  32"
    )
    texts = [text] * ITEM_NUM
    line = "*Text* with expected len \\-  32\n"
    lines = ["".join([line] * (ITEM_NUM-1)), line]
    markdown_messages = into_markdown_messages(texts)

    print(lines)

    expected = lines[0]
    actual = markdown_messages[0]
    assert actual == expected

    expected = lines[1]
    actual = markdown_messages[1]
    assert actual == expected
