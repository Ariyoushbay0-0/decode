"""
search_engine.py
-----------------
Beam Search + A* (بند ۱)، حالا با چند بهینه‌سازی سرعت که بدون از دست دادن
هیچ Flagی، حجم محاسبات را کم می‌کنند:

1) verbose پیش‌فرض خاموش است (پرینت هر گره خودش هزینه‌ی زیادی دارد).
2) visited بر اساس فقط «متن» است (نه متن+عمق). چون هزینه با عمق یکنواخت
   افزایش می‌یابد، دیدنِ دوباره‌ی همان متن در عمق بیشتر همیشه بدتر است؛
   حذفش هیچ مسیر برنده‌ای را از دست نمی‌دهد، فقط تکرار بی‌فایده را می‌گیرد.
3) وقتی متنی از قبل تقریبا برابر یک Flag معتبر است (strong_match)، دیگر از
   آن گره منشعب نمی‌شویم - چون ادامه‌ی Decode روی یک Flag تمیز فقط زباله
   تولید می‌کند (مثل ۲۵ نسخه‌ی Caesar روی خودِ Flag پیدا‌شده).
4) Caesar/ROT13 فقط وقتی روی متن اجرا می‌شوند که متن عمدتاً حرفی باشد
   (alpha_ratio بالا) - چون این Decoderها فقط روی متن حرفی معنا دارند و
   اجرای‌شان روی گارباژ باینری صرفاً اتلاف وقت است.
5) به‌جای sort کامل روی کل candidateهای هر عمق، از heapq.nsmallest استفاده
   می‌شود که وقتی beam_width << تعداد کل candidateها، سریع‌تر است.

منطق اصلی (g/h/f، Adaptive Beam، جمع‌آوری همه‌ی Candidateها) دست‌نخورده مانده.
"""

import heapq

from decoder_weights import path_cost
from scoring import score_text, printable_ratio

# نام آن Decoderهایی که فقط روی متن معنادار (نه گارباژ باینری خالص) ارزش دارند.
# توجه: گیت باید فقط گارباژ باینری واقعی (بایت‌های >126 یا کنترلی) را فیلتر کند،
# نه رشته‌های Hex/Base64 که رقم زیاد دارند ولی کاملا معتبرند - وگرنه زنجیره‌هایی
# مثل «...Base64 -> ROT13 -> Hex...» که ROT13 روی متن Hex اجرا می‌شود، اشتباهاً
# فیلتر می‌شوند (این باگ در تست اول این نسخه پیدا و همینجا اصلاح شد).
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

                # Caesar/ROT13 فقط وقتی اجرا شود که متن گارباژ باینری خالص نباشد
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

                # اگر این متن خودش تقریبا کامل یک Flag معتبر است، دیگر لازم
                # نیست رویش Decode بیشتری امتحان کنیم (صرفه‌جویی محاسباتی).
                if self.flag_validator.strong_match(text):
                    continue

                children = self._expand(text, path)
                next_candidates.extend(children)

            if not next_candidates:
                break

            found_new_flags = len(self.flag_validator.candidates) > candidates_before

            if not found_new_flags:
                # هیچ Candidate جدیدی پیدا نشد -> Beam را موقتا بزرگ‌تر کن (fallback به BFS)
                current_beam = min(current_beam + self.adaptive_growth, self.max_beam_width)
            else:
                current_beam = self.beam_width

            # به‌جای sort کامل، فقط top-K را با nsmallest بگیر (سریع‌تر برای beam کوچک)
            if len(next_candidates) > current_beam:
                current_layer = heapq.nsmallest(current_beam, next_candidates, key=lambda c: c[0])
            else:
                next_candidates.sort(key=lambda c: c[0])
                current_layer = next_candidates

            depth += 1

        return self.flag_validator.best_candidates()
