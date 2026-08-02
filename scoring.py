"""
scoring.py
"""

import re
import math
import string

FLAG_PATTERNS = [
    r"picoCTF\{[^{}]{1,300}\}",
    r"flag\{[^{}]{1,300}\}",
    r"CTF\{[^{}]{1,300}\}",
    r"[A-Za-z0-9_]{2,20}\{[^{}]{1,300}\}", 
]

COMMON_FLAG_CHARS = set("_-")


def printable_ratio(text: str) -> float:
    if not text:
        return 0.0
    printable = sum(c in string.printable for c in text)
    return printable / len(text)


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0

    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1

    length = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)

    return entropy


def readability_score(text: str) -> float:
    """نسبت حروف/فاصله/رقم به کل طول متن؛ متن باینری گارباژ این عدد را پایین می‌آورد."""
    if not text:
        return 0.0

    good_chars = sum(c.isalnum() or c in " _-{}" for c in text)
    return good_chars / len(text)


def flag_pattern_bonus(text: str) -> float:
    bonus = 0.0
    for pattern in FLAG_PATTERNS:
        if re.search(pattern, text):
            bonus += 300
    return bonus


def common_char_bonus(text: str) -> float:
    bonus = 0.0
    for c in text:
        if c in COMMON_FLAG_CHARS:
            bonus += 2
        elif c.isalnum():
            bonus += 0.4
    return bonus


def garbage_penalty(text: str) -> float:
    if not text:
        return 0.0

    bad = sum(
        (ord(c) > 126) or (ord(c) < 32 and c not in "\n\r\t")
        for c in text
    )
    return bad * 40


def entropy_penalty(text: str) -> float:
    """متن انگلیسی/فلگ‌مانند معمولا انتروپی ۳.۵ تا ۴.۵ بیت/کاراکتر دارد.
    باینری/رندوم گارباژ معمولا بالای ۵.۵ می‌رود -> جریمه می‌شود."""
    ent = shannon_entropy(text)
    if ent > 5.5:
        return (ent - 5.5) * 60
    return 0.0


def length_bonus(text: str) -> float:
    n = len(text)
    if 10 < n < 300:
        return 30.0
    if n >= 300:
        return -min((n - 300) * 0.5, 100)
    return 0.0


def alpha_ratio(text: str) -> float:
    """نسبت حروف الفبا/فاصله به کل طول. برای gate کردن Decoderهای گران (Caesar/ROT13)
    استفاده می‌شود: این Decoderها فقط روی متن حرفی معنا دارند، نه روی گارباژ باینری."""
    if not text:
        return 0.0
    letters = sum(c.isalpha() or c.isspace() for c in text)
    return letters / len(text)


def score_text(text: str) -> float:
    """امتیاز نهایی یک خروجی Decode. عدد بالاتر = محتمل‌تر است که به Flag نزدیک باشد."""
    if not text:
        return -9999.0

    score = 0.0
    score += printable_ratio(text) * 200
    score += readability_score(text) * 150
    score += flag_pattern_bonus(text)
    score += common_char_bonus(text)
    score += length_bonus(text)
    score -= garbage_penalty(text)
    score -= entropy_penalty(text)

    return round(score, 2)
