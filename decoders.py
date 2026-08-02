"""
decoders.py
------------
تمام Decoderها دقیقاً همان منطق نسخه‌ی قبلی را دارند (چیزی حذف نشده).
این فایل فقط Decoderها را جدا نگه می‌دارد تا ماژولار بمانند.
"""

import re
import base64
import codecs
import urllib.parse
import quopri
import html


def decode_base64(data):
    results = []

    try:
        padding = "=" * (-len(data) % 4)
        decoded = base64.b64decode(data + padding, validate=False).decode("utf-8")
        results.append(("Base64", decoded))
    except Exception:
        pass

    try:
        padding = "=" * (-len(data) % 4)
        decoded = base64.urlsafe_b64decode(data + padding).decode("utf-8")
        if ("Base64URL", decoded) not in results:
            results.append(("Base64URL", decoded))
    except Exception:
        pass

    return results


def decode_hex(data):
    try:
        cleaned = re.sub(r"0x|\\x|\s", "", data, flags=re.IGNORECASE)
        return [("Hex", bytes.fromhex(cleaned).decode("utf-8"))]
    except Exception:
        return []


def decode_binary(data):
    try:
        cleaned = data.replace(" ", "")

        if not re.fullmatch(r"[01]+", cleaned):
            return []

        chars = [chr(int(cleaned[i:i + 8], 2)) for i in range(0, len(cleaned), 8)]
        return [("Binary", "".join(chars))]
    except Exception:
        return []


def decode_base32(data):
    try:
        padding = "=" * (-len(data) % 8)
        return [("Base32", base64.b32decode(data + padding).decode())]
    except Exception:
        return []


def decode_base85(data):
    try:
        return [("Base85", base64.b85decode(data).decode())]
    except Exception:
        return []


def decode_unicode_escape(data):
    try:
        decoded = codecs.decode(data, "unicode_escape")
        if decoded != data:
            return [("UnicodeEscape", decoded)]
    except Exception:
        pass

    return []


def decode_url(data):
    try:
        result = urllib.parse.unquote(data)
        if result != data:
            return [("URL", result)]
    except Exception:
        pass

    return []


def decode_reverse(data):
    return [("Reverse", data[::-1])]


def decode_rot13(data):
    try:
        return [("ROT13", codecs.decode(data, "rot_13"))]
    except Exception:
        return []


def decode_html(data):
    try:
        decoded = html.unescape(data)
        if decoded != data:
            return [("HTML", decoded)]
    except Exception:
        pass

    return []


def decode_quoted_printable(data):
    try:
        return [("QuotedPrintable", quopri.decodestring(data).decode())]
    except Exception:
        return []


def decode_decimal(data):
    try:
        chars = [chr(int(x)) for x in data.split()]
        return [("DecimalASCII", "".join(chars))]
    except Exception:
        return []


def decode_octal(data):
    try:
        chars = [chr(int(x, 8)) for x in data.split()]
        return [("OctalASCII", "".join(chars))]
    except Exception:
        return []


def decode_caesar(data):
    results = []

    for shift in range(1, 26):
        output = ""

        for ch in data:
            if ch.isalpha():
                base = ord("A") if ch.isupper() else ord("a")
                output += chr((ord(ch) - base + shift) % 26 + base)
            else:
                output += ch

        results.append((f"ROT{shift}", output))

    return results


# لیست Decoderها - دقیقا همان‌هایی که در نسخه‌ی قبلی بودند
decoders = [
    decode_base64,
    decode_base32,
    decode_base85,
    decode_hex,
    decode_binary,
    decode_decimal,
    decode_octal,
    decode_url,
    decode_unicode_escape,
    decode_html,
    decode_quoted_printable,
    decode_reverse,
    decode_rot13,
    decode_caesar,
]
