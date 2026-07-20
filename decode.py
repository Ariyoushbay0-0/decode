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
# Decoders
# =========================

def decode_base64(data):
    try:
        return base64.b64decode(data).decode()
    except:
        return None


def decode_hex(data):
    try:
        return bytes.fromhex(data).decode()
    except:
        return None


def decode_url(data):
    try:
        return urllib.parse.unquote(data)
    except:
        return None


def decode_rot13(data):
    try:
        return codecs.decode(data, "rot13")
    except:
        return None



decoders = {
    "Base64": decode_base64,
    "Hex": decode_hex,
    "URL": decode_url,
    "ROT13": decode_rot13
}



# =========================
# BFS Decoder Engine
# =========================

def auto_decode(start_text, max_depth=8):

    queue = deque()

    # text , decode path
    queue.append(
        (start_text, [])
    )


    visited = set()


    while queue:

        text, path = queue.popleft()


        # depth limit
        if len(path) >= max_depth:
            continue


        # جلوگیری از تکرار
        if text in visited:
            continue

        visited.add(text)



        # چک فلگ
        match = regex.search(text)

        if match:

            print("\n================")
            print("FOUND!")

            print("\nDecode Path:")

            for step in path:
                print(" ↓", step)

            print("\nFlag:")
            print(match.group())

            return match.group()



        # تست Decoderها
        for name, decoder in decoders.items():

            output = decoder(text)


            if output and output != text:


                queue.append(
                    (
                        output,
                        path + [name]
                    )
                )


    print("\nFlag not found")



# =========================
# Run
# =========================

auto_decode(encoded_text)
