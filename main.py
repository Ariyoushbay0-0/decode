"""
main.py
-------
نقطه‌ی ورود پروژه. هدف: پیدا کردن *همه‌ی* Flagهای ممکن، در سریع‌ترین
حالت ممکن (verbose خاموش، dedup روی متن، gate کردن Caesar/ROT13 روی
گارباژ، توقف زودهنگام از یک گره‌ی از قبل حل‌شده - همه در search_engine.py).
"""

import re
import time

from decoders import decoders
from flag_validator import FlagValidator
from search_engine import BeamAStarSearch


def print_results(results, elapsed, nodes_explored):
    print(f"\n(زمان اجرا: {elapsed:.3f}s | گره‌های بررسی‌شده: {nodes_explored})")

    if not results:
        print("\nFlag not found")
        return

    print(f"\n================ RESULTS ({len(results)} flag یافت شد) ================")

    for i, r in enumerate(results, 1):
        print(f"\nRank {i} | Score: {r['score']}")
        print("Path:")
        for step in r["path"]:
            print("  ↓", step)
        print("Flag:")
        print(" ", r["flag"])


def main():
    flag_prefix = input("Flag format: ").strip()
    flag_prefix = re.sub(r"\{.*\}$", "", flag_prefix)
    print(flag_prefix)

    encoded_text = input("Encoded text: ").strip()

    validator = FlagValidator(flag_prefix)

    engine = BeamAStarSearch(
        decoders=decoders,
        flag_validator=validator,
        beam_width=40,          # چند مسیر برتر در هر عمق نگه داشته شود
        max_depth=20,           # حداکثر عمق Decode
        max_total_nodes=20000,  # سقف کلی گره‌ها برای جلوگیری از انفجار
        adaptive_growth=25,     # اگر عمقی نتیجه‌ای نداد، beam چقدر بزرگ شود
        max_beam_width=400,
        verbose=False,          # خاموش برای سرعت؛ برای دیباگ True کن
    )

    start = time.perf_counter()
    results = engine.run(encoded_text)  # همه‌ی Flagهای یافت‌شده (top_n=None داخل validator هم قابل استفاده است)
    elapsed = time.perf_counter() - start

    # اگر خواستی واقعا *همه*‌ی Candidateها (نه فقط ۵ تای برتر) را ببینی:
    all_results = validator.best_candidates(top_n=None)

    print_results(all_results, elapsed, engine.explored_nodes)


if __name__ == "__main__":
    main()
