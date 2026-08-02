"""
search_engine.py

"""

import heapq

from decoder_weights import path_cost
from scoring import score_text, printable_ratio


_ROT_DECODERS = {"ROT13"} | {f"ROT{i}" for i in range(1, 26)}
_PRINTABLE_GATE_THRESHOLD = 0.95


class BeamAStarSearch:
    def __init__(
        self,
        decoders,
        flag_validator,
        beam_width=40,
        max_depth=20,
        max_total_nodes=20000,
        adaptive_growth=25,
        max_beam_width=400,
        verbose=False,
    ):
        self.decoders = decoders
        self.flag_validator = flag_validator
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.max_total_nodes = max_total_nodes
        self.adaptive_growth = adaptive_growth
        self.max_beam_width = max_beam_width
        self.verbose = verbose

        self.visited = set()
        self.explored_nodes = 0

    def _expand(self, text, path):
        """یک گره را باز می‌کند و فرزندانش را برمی‌گرداند: (f, text, path, h)."""
        children = []
        text_is_probably_textual = printable_ratio(text) >= _PRINTABLE_GATE_THRESHOLD

        for decoder in self.decoders:
            try:
                results = decoder(text)
            except Exception:
                continue

            for name, result in results:
                if not result or result == text:
                    continue


                if name in _ROT_DECODERS and not text_is_probably_textual:
                    continue

                if result in self.visited:
                    continue
                self.visited.add(result)

                new_path = path + [name]
                g = path_cost(new_path)
                h = score_text(result)
                f = g - h

                children.append((f, result, new_path, h))

        return children

    def run(self, start_text):
        current_layer = [(0, start_text, [], score_text(start_text))]
        self.visited.add(start_text)
        depth = 0
        current_beam = self.beam_width

        while current_layer and depth < self.max_depth and self.explored_nodes < self.max_total_nodes:
            next_candidates = []
            candidates_before = len(self.flag_validator.candidates)

            for f, text, path, h in current_layer:
                if self.explored_nodes >= self.max_total_nodes:
                    break

                self.explored_nodes += 1

                self.flag_validator.check(text, path)

                if self.verbose:
                    print(path, "score:", h, "=>", repr(text[:50]))


                if self.flag_validator.strong_match(text):
                    continue

                children = self._expand(text, path)
                next_candidates.extend(children)

            if not next_candidates:
                break

            found_new_flags = len(self.flag_validator.candidates) > candidates_before

            if not found_new_flags:
                
                current_beam = min(current_beam + self.adaptive_growth, self.max_beam_width)
            else:
                current_beam = self.beam_width


            if len(next_candidates) > current_beam:
                current_layer = heapq.nsmallest(current_beam, next_candidates, key=lambda c: c[0])
            else:
                next_candidates.sort(key=lambda c: c[0])
                current_layer = next_candidates

            depth += 1

        return self.flag_validator.best_candidates()
