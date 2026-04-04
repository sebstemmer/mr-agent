from app.channels.src.split_message import split_message


def test_text_within_limit_returns_single_message():
    result = split_message(text="hello world", max_length=100)

    assert result == ["hello world"]


def test_splits_on_paragraph_boundary():
    text = "paragraph one\n\nparagraph two\n\nparagraph three"
    result = split_message(text=text, max_length=20)

    assert result == ["paragraph one", "paragraph two", "paragraph three"]


def test_groups_paragraphs_that_fit():
    text = "short\n\nalso short\n\nthird one that is much longer"
    result = split_message(text=text, max_length=30)

    assert result == ["short\n\nalso short", "third one that is much longer"]


def test_all_separator_levels():
    normal = "hello"
    long_word = "a" * 25
    needs_line_split = "line one\nline two\nline three"
    needs_word_split = "the quick brown fox jumps over"
    text = f"{normal}\n\n{long_word}\n\n{needs_line_split}\n\n{needs_word_split}"

    result = split_message(text=text, max_length=15)

    assert result == [
        "hello",
        "aaaaaaaaaaaaaaa", "aaaaaaaaaa",
        "line one", "line two", "line three",
        "the quick brown", "fox jumps over",
    ]
