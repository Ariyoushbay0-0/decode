import re 
import base64
import codecs
import urllib.parse
from collections import deque

#______________________________
# input
#______________________________

flag_prefix = input("Flag format: ").strip()

flag_prefix = re.sub(r"\{.*\}$", "", flag_prefix)
print(flag_prefix)

encoded_text = input("Encoded text: ").strip()

#______________________________
# Flag Regex
#______________________________

regex = re.compile(rf"{re.escape(flag_prefix)}\{{.*?\}}")

#______________________________
# Decoders
#______________________________

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


def decode_caesar(data):

    results = []

    for shift in range(1, 26):

        output = ""

        for ch in data:

            if ch.isalpha():

                base = ord("A") if ch.isupper() else ord("a")

                output += chr(
                    (ord(ch) - base + shift) % 26 + base
                )

            else:
                output += ch

        results.append(
            (f"ROT{shift}", output)
        )

    return results

decoders = [
    decode_base64,
    decode_hex,
    decode_url,
    decode_caesar
]


# ___________________________
# BFS Decoder Engine
# ___________________________

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
        # تست Decoderها
        for decoder in decoders:

            outputs = decoder(text)

            for name, result in outputs:

                if result and result != text:

                    print(
                        path + [name],
                        "=>",
                        repr(result[:80])
                        )

                    queue.append(
                        (
                            result,
                            path + [name]
                        )
                    )


    print("\nFlag not found")



# ___________________________
# Run
# ___________________________

auto_decode(encoded_text)
