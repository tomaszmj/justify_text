#!/usr/bin/python
import sys
import logging
import time
from typing import List


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if len(sys.argv) != 2:
        logging.error(f"usage: {sys.argv[0]} <line length - integer> (text will be read from stdin)")
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
            words_in_line = line.split()
            for word in words_in_line:
                if len(word) > line_length:
                    logging.error(f"text cannot be justified - word {word} is too long for line length {line_length}")
                    return
            words.extend(words_in_line)
    except KeyboardInterrupt:  # text should end with EOF, but we also allow ctrl+C
        logging.warning("KeyboardInterrupt received, reading text stopped (last line may be missing)")
    logging.info("text has been read")
    try:
        text = justify_text(words, line_length)
    except BaseException as e:
        logging.error(f"failed to justify text: {e}")
        raise
    print("\n".join(text))


# justify_text for given text and line_length returns 
# justified list of lines. For example:
# justify_text(["Hello!", "Nice", "to", "meet", "you."], 12)
# returns ["Hello!  Nice", "to meet you."].
def justify_text(words: List[str], line_length: int) -> List[str]:
    t0 = time.time()
    min_badness = [-1] * len(words) + [0]  # + [0] to satisfy min_badness[end + 1] for end = len(words)-1
    best_end = [len(words)-1] * len(words)
    for begin in range(len(words)-1, -1, -1):
        current_line_min_length = 0
        for end in range(begin, len(words)):
            current_line_min_length += len(words[end])
            if end - begin > 0:
                current_line_min_length += 1  # space between words
            if current_line_min_length > line_length:
                break
            # Min badness of current text split is sum of:
            # - badness of the current line,
            # - min badness of "recursive" calls for whole remaining text.
            # Here instead of recursive calls we can just use DP table min_badness.
            badness = get_badness(end - begin + 1, line_length, current_line_min_length) + min_badness[end + 1]
            if min_badness[begin] == -1 or badness < min_badness[begin]:
                min_badness[begin] = badness
                best_end[begin] = end
    begin = 0
    result = []
    while begin < len(words):
        end = best_end[begin]
        words_tmp = words[begin : end+1]
        min_length = sum(len(w) for w in words_tmp) + len(words_tmp) - 1
        result.append(words_to_line(words_tmp, line_length, min_length))
        begin = end + 1
    td = time.time() - t0
    logging.info(f"justify_text done, badness: {min_badness[0]}, execution time {td} s")
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
        return None
    additional_spaces = line_length - current_line_min_length
    result = 0
    if words_in_line_count == 1:
        result = additional_spaces**2
    else:
        min_additional_spaces_per_w = additional_spaces // (words_in_line_count - 1)
        mod = additional_spaces % (words_in_line_count - 1)
        result = (min_additional_spaces_per_w + 1)**2 * mod + min_additional_spaces_per_w**2 * (words_in_line_count - 1 - mod)
    return result


if __name__ == "__main__":
    main()
