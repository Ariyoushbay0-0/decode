"""
decoder_weights.py
-------------------
Decoder Weight System (بند ۳).
هر Decoder یک "هزینه" دارد؛ Decoderهای رایج و قطعی (Base64، Hex ...) ارزان‌ترند
و Decoderهای احتمالی/گسترده (Caesar، ROT13، Reverse) گران‌ترند تا در Search
(A* / Beam Search) مسیرهای منطقی زودتر بررسی شوند.
"""

DEFAULT_COST = 6

decoder_cost = {
    "Base64": 1,
    "Base64URL": 1,

    "Hex": 1,

    "Base32": 2,
    "Base85": 2,

    "Binary": 2,
    "DecimalASCII": 2,
    "OctalASCII": 3,

    "URL": 2,

    "UnicodeEscape": 3,
    "HTML": 2,
    "QuotedPrintable": 2,

    "Reverse": 3,

    "ROT13": 4,
}

# Caesar ROT1..ROT25 (ROT13 override می‌شود چون در دیکشنری بالا صریح تعریف شده)
for shift in range(1, 26):
    key = f"ROT{shift}"
    decoder_cost.setdefault(key, 5)


def get_cost(decoder_name: str) -> int:
    return decoder_cost.get(decoder_name, DEFAULT_COST)


def path_cost(path):
    """هزینه‌ی تجمعی یک مسیر Decode (g(n) در A*)."""
    return sum(get_cost(step) for step in path)
