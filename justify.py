#!/usr/bin/python
import sys
import logging
import time
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
        raise
    print("\n".join(text))
    logging.info("text justified successfully")


# justify_text for given text and line_length returns 
# justified list of lines. For example:
# justify_text(["Hello!", "Nice", "to", "meet", "you."], 12)
# returns ["Hello!  Nice", "to meet you."].
# If length of any word is longer than
# line_length, it will raise an exception.
def justify_text(words: List[str], line_length: int) -> List[str]:
    if len(words) == 0:
        return []
    for word in words:
        if len(word) > line_length:
            raise BaseException(f"word {word} is too long for line length {line_length}")
    justify_text_dp(words, line_length)
    return justify_text_bruteforce(words, line_length)
    # return justify_text_greedy(words, line_length)


def justify_text_greedy(words: List[str], line_length: int) -> List[str]:
    t0 = time.time()
    result = []
    words_tmp = []
    current_line_min_length = 0
    badness = 0
    for word in words:
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
    td = time.time() - t0
    logging.info(f"justify_text_greedy badness: {badness}, execution time {td}")
    return result


def justify_text_bruteforce(words: List[str], line_length: int) -> List[str]:
    t0 = time.time()
    best_subset = 0
    best_badness = None
    for subset in range(0, 2**(len(words) - 1)):
        subset = subset | (1 << len(words)-1)  # each subset must have 1 on the most significant bit
        begin = 0
        badness = 0
        for i in range(len(words)):
            bitmask = 1 << i
            if not subset & bitmask:
                continue
            words_tmp = words[begin:i+1]
            min_length = sum(len(w) for w in words_tmp) + len(words_tmp) - 1
            if min_length > line_length or len(words_tmp) == 0:
                badness = None
                break
            badness += get_badness(len(words_tmp), line_length, min_length)
            begin = i + 1
        if badness is not None and (best_badness is None or badness < best_badness):
            best_subset = subset
            best_badness = badness
    if best_badness is None:  # sanity check
        raise BaseException("justify_text_bruteforce failed to find anything")
    result = []
    begin = 0
    for i in range(len(words)):
        bitmask = 1 << i
        if not best_subset & bitmask:
            continue
        words_tmp = words[begin:i+1]
        min_length = sum(len(w) for w in words_tmp) + len(words_tmp) - 1
        result.append(words_to_line(words_tmp, line_length, min_length))
        begin = i + 1
    td = time.time() - t0
    logging.info(f"justify_text_bruteforce badness: {best_badness}, execution time {td}")
    return result


def justify_text_dp(words: List[str], line_length: int) -> List[str]:
    print(justify_text_dp_iteration(words, line_length, 0, {}))
    return []


def justify_text_dp_iteration(words: List[str], line_length: int, begin: int, state: dict) -> int:
    logging.debug(f"justify_text_dp_iteration({len(words)} words, {line_length}, {begin}, state) ...")
    if begin == len(words):
        logging.debug(f"justify_text_dp_iteration({len(words)} words, {line_length}, {begin}, state) -> 0")
        return 0
    if begin in state:
        logging.debug(f"justify_text_dp_iteration({len(words)} words, {line_length}, {begin}, state) -> {state[begin]}")
        return state[begin]
    current_line_min_length = 0
    min_badness = None
    min_badness_end = -1
    for end in range(begin, len(words)):
        current_line_min_length += len(words[end])
        if end - begin > 0:
            current_line_min_length += 1  # space between words
        if current_line_min_length > line_length:
            logging.debug(f"{current_line_min_length} > {line_length}, begin {begin}, end {end}")
            break
        logging.debug(f"justify_text_dp_iteration calls get_badness, begin {begin}, end {end}")
        badness1 = get_badness(end - begin + 1, line_length, current_line_min_length)
        badness2 = justify_text_dp_iteration(words, line_length, end + 1, state)
        badness = badness1 + badness2
        if min_badness is None or badness < min_badness:
            min_badness = badness
            min_badness_end = end
    state[begin] = min_badness
    logging.debug(f"justify_text_dp_iteration({len(words)} words, {line_length}, {begin}, state) -> {min_badness}")
    return min_badness


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
    logging.debug(f"get_badness({words_in_line_count}, {line_length}, {current_line_min_length}) -> {result}")
    return result


if __name__ == "__main__":
    main()
