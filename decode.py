import re
import base64
import codecs
import urllib.parse
from collections import deque


# =========================
# Input
# =========================

flag_prefix = input("Flag format: ").strip()
encoded_text = input("Encoded text: ").strip()


# =========================
# Flag Regex
# =========================

regex = re.compile(
    rf"{re.escape(flag_prefix)}\{{.*?\}}"
)


# =========================
# Decoder Functions
# =========================

def decode_base64(data):
    try:
        return [("Base64", base64.b64decode(data).decode())]
    except:
        return []


def decode_hex(data):
    try:
        return [("Hex", bytes.fromhex(data).decode())]
    except:
        return []


def decode_url(data):
    try:
        result = urllib.parse.unquote(data)

        if result != data:
            return [("URL", result)]

    except:
        pass

    return []


def decode_rot13(data):
    try:
        return [
            ("ROT13", codecs.decode(data, "rot13"))
        ]
    except:
        return []


def decode_caesar(data):

    results = []

    for shift in range(1, 26):

        output = ""

        for char in data:

            if char.isalpha():

                start = ord('A') if char.isupper() else ord('a')

                output += chr(
                    (ord(char) - start + shift) % 26 + start
                )

            else:
                output += char


        results.append(
            (f"Caesar-{shift}", output)
        )


    return results



# =========================
# Decoder List
# =========================

decoders = [
    decode_base64,
    decode_hex,
    decode_url,
    decode_rot13,
    decode_caesar
]


# =========================
# BFS Engine
# =========================

def auto_decode(start_text, max_depth=8):

    queue = deque()

    queue.append(
        (
            start_text,
            []
        )
    )


    visited = set()


    while queue:

        text, path = queue.popleft()


        # محدود کردن عمق
        if len(path) >= max_depth:
            continue


        # جلوگیری از حلقه
        if text in visited:
            continue

        visited.add(text)



        # بررسی فلگ
        match = regex.search(text)


        if match:

            print("\n================")
            print("FOUND!")

            print("\nDecode Path:")

            for step in path:
                print(" ↓", step)


            print("\nFlag:")
            print(match.group())

            return



        # اجرای Decoderها

        for decoder in decoders:

            outputs = decoder(text)


            for name, result in outputs:


                if result and result != text:

                    queue.append(
                        (
                            result,
                            path + [name]
                        )
                    )



    print("\nFlag not found")



# =========================
# Run
# =========================

auto_decode(encoded_text)
