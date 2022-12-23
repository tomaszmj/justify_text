#!/usr/bin/python
import sys
import logging
from typing import List


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if len(sys.argv) != 2:
        logging.error("expected 1 argument - line length (text will be read from stdin)")
        return
    try:
        line_length = int(sys.argv[1])
    except ValueError:
        logging.error(f"invalid line length format, expected integer, got {sys.argv[1]}")
        return
    words = []
    logging.info("reading text from stdin ...")
    try:
        for line in sys.stdin:
            line = line.strip()
            words.extend(line.split())
    except KeyboardInterrupt:  # text should end with EOF, but we also allow ctrl+C
        logging.warning("KeyboardInterrupt received, reading text stopped (last line may be missing)")
    logging.info("text has been read")
    try:
        text = justify_text(words, line_length)
    except BaseException as e:
        logging.error(f"failed to justify text: {e}")
        return
    print("\n".join(text))
    logging.info("text justified successfully")


# justify_text for given text and line_length returns 
# justified list of lines. For example:
# justify_text(["Hello!", "Nice", "to", "meet", "you."], 12)
# returns ["Hello!  Nice", "to meet you."].
# If length of any word is longer than
# line_length, it will raise an exception.
def justify_text(words: List[str], line_length: int) -> List[str]:
    return justify_text_greedy(words, line_length)


def justify_text_greedy(words: List[str], line_length: int) -> List[str]:
    result = []
    words_tmp = []
    current_line_min_length = 0
    badness = 0
    for word in words:
        if len(word) > line_length:
            raise BaseException(f"word {word} is too long for line length {line_length}")
        new_line_min_length = current_line_min_length + len(word) 
        if len(words_tmp) > 0:
            new_line_min_length += 1
        if new_line_min_length > line_length:
            badness += get_badness(len(words_tmp), line_length, current_line_min_length)
            result.append(words_to_line(words_tmp, line_length, current_line_min_length))
            current_line_min_length = len(word)
            words_tmp = [word]
        else:
            words_tmp.append(word)
            current_line_min_length = new_line_min_length
    if len(words_tmp) > 0:
        badness += get_badness(len(words_tmp), line_length, current_line_min_length)
        result.append(words_to_line(words_tmp, line_length, current_line_min_length))
    logging.info(f"justify_text_greedy badness: {badness}")
    return result


def words_to_line(words: List[str], line_length: int, current_line_min_length: int) -> str:
    if len(words) == 0:
        raise BaseException("words_to_line called with empty list of words")
    if len(words) == 1:
        return words[0] + " " * (line_length - current_line_min_length)
    additional_spaces = line_length - current_line_min_length
    if additional_spaces < 0:
        raise BaseException(f"line_length {line_length} is too short for words {words}")
    min_additional_spaces_per_w = additional_spaces // (len(words) - 1)
    mod = additional_spaces % (len(words) - 1)
    for i in range(1, len(words)):
        spaces = min_additional_spaces_per_w
        if mod > 0:
            spaces += 1
            mod -=1
        words[i] = " " * spaces + words[i]
    return " ".join(words)


# get_badness returns how "bad" justified line of text would be.
# Badness is defined as sum of squares of all additional spaces,
# but it could be calculated in some other way as well.
def get_badness(words_in_line_count: int, line_length: int, current_line_min_length: int) -> int:
    if words_in_line_count == 0:
        raise BaseException("get_badness called with empty list of words")
    additional_spaces = line_length - current_line_min_length
    result = 0
    if words_in_line_count == 1:
        result = additional_spaces**2
    else:
        min_additional_spaces_per_w = additional_spaces // (words_in_line_count - 1)
        mod = additional_spaces % (words_in_line_count - 1)
        result = (min_additional_spaces_per_w + 1)**2 * mod + min_additional_spaces_per_w**2 * (words_in_line_count - 1 - mod)
    logging.debug(f"get_badness({words_in_line_count}, {line_length}, {current_line_min_length}) -> {result}")
    return result


if __name__ == "__main__":
    main()
