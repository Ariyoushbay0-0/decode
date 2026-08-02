"""
main.py
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
        beam_width=40,          
        max_depth=20,           
        max_total_nodes=2000
        adaptive_growth=25,     
        max_beam_width=400,
        verbose=False,          
    )

    start = time.perf_counter()
    results = engine.run(encoded_text)  
    elapsed = time.perf_counter() - start

    all_results = validator.best_candidates(top_n=None)

    print_results(all_results, elapsed, engine.explored_nodes)


if __name__ == "__main__":
    main()
