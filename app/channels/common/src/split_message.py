def _find_delta(
        chunks: list[str],
        start: int,
        max_length: int,
        separator: str
) -> int:
    """Find how many additional chunks can be included starting from `start` without exceeding `max_length`.

    Returns delta such that chunks[start:start + delta + 1] joined by `separator` fits within max_length.
    Returns -1 if the chunk at `start` alone exceeds max_length.
    """
    # noinspection PyTypeChecker
    if len(chunks[start]) > max_length:
        return -1

    # noinspection PyTypeChecker
    candidate = chunks[start]

    # noinspection PyTypeChecker
    for i in range(start + 1, len(chunks)):
        next_candidate = candidate + separator + chunks[i]
        if len(next_candidate) > max_length:
            return i - 1 - start
        candidate = next_candidate

    return len(chunks) - 1 - start


def _split_message_with_separators(
        text: str,
        max_length: int,
        separators: list[str],
) -> list[str]:
    if not separators:
        # noinspection PyTypeChecker
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    # noinspection PyTypeChecker
    separator = separators[0]
    remaining_separators = separators[1:]
    chunks = text.split(separator)
    messages = []
    start = 0

    while start < len(chunks):
        delta = _find_delta(
            chunks=chunks,
            start=start,
            max_length=max_length,
            separator=separator,
        )
        if delta == -1:
            messages.extend(
                _split_message_with_separators(
                    text=chunks[start],
                    max_length=max_length,
                    separators=remaining_separators,
                )
            )
            start += 1
            continue

        messages.append(separator.join(chunks[start:start + delta + 1]))
        start = start + delta + 1

    return messages


def split_message(text: str, max_length: int) -> list[str]:
    if len(text) <= max_length:
        return [text]

    return _split_message_with_separators(
        text=text,
        max_length=max_length,
        separators=["\n\n", "\n", " "],
    )
