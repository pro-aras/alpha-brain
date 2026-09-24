"""names.py — A LETTER/DIGIT/SIGN'S NAME (B1-PREREG.md §2.3).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:5x +0400 — B1-PREREG.md §9 row 1, step 2 (the world).

"A letter's NAME is its lower-case letter as the ear's word ("a" for both A and a) — case is not in the
name; the digits' names are zero one two three four five six seven eight nine (the ear takes letters a-z
only; genome/world.py:encode_word)." (§2.3)
"""
from __future__ import annotations

UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER = "abcdefghijklmnopqrstuvwxyz"
DIGIT_CHARS = "0123456789"
DIGIT_NAMES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
PLANT_NAME = "zog"   # U6's invented sign (§2.3: "letters only, <= 8, not a B1 name")


class NameError_(Exception):
    pass


def letter_name(char: str) -> str:
    """§2.3: case is not in the name — "a" for both "A" and "a"."""
    if len(char) != 1 or char not in UPPER + LOWER:
        raise NameError_(f"not a single letter: {char!r}")
    return char.lower()


def digit_name(digit_char: str) -> str:
    if digit_char not in DIGIT_CHARS:
        raise NameError_(f"not a single digit character: {digit_char!r}")
    return DIGIT_NAMES[DIGIT_CHARS.index(digit_char)]


def name_of(char: str, script: str) -> str:
    """Dispatch by script: 'latin-upper'/'latin-lower' -> letter_name; 'digits' -> digit_name."""
    if script in ("latin-upper", "latin-lower"):
        return letter_name(char)
    if script == "digits":
        return digit_name(char)
    raise NameError_(f"names.name_of: unknown script {script!r}")
