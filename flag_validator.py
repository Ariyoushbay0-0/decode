"""
flag_validator.py
------------------
Flag Detection قوی‌تر (بند ۴).
به‌جای برگرداندن اولین Flag، تمام Candidateهای ممکن در طول جستجو جمع‌آوری
می‌شوند، هرکدام امتیاز می‌گیرند و در پایان بهترین‌ها نمایش داده می‌شوند.
"""

import re
from scoring import score_text


def build_specific_regex(flag_prefix: str):
    if flag_prefix:
        return re.compile(rf"{re.escape(flag_prefix)}\{{.*?\}}")
    # اگر prefix خالی بود، فقط الگوی عمومی استفاده می‌شود
    return re.compile(r"(?!x)x")  # regex که هرگز match نمی‌کند


# الگوی عمومی PREFIX{...} برای موقعی که کاربر format دقیق را نمی‌داند
GENERIC_FLAG_REGEX = re.compile(r"[A-Za-z0-9_]{2,20}\{[^{}]{1,300}\}")


class FlagValidator:
    def __init__(self, flag_prefix: str):
        self.flag_prefix = flag_prefix
        self.specific_regex = build_specific_regex(flag_prefix)
        self.generic_regex = GENERIC_FLAG_REGEX

        self.seen = set()
        self.candidates = []  # هر آیتم: {"flag", "path", "score"}

    def _extract(self, text: str):
        found = set()

        for m in self.specific_regex.finditer(text):
            found.add(m.group())

        for m in self.generic_regex.finditer(text):
            found.add(m.group())

        return found

    def check(self, text: str, path):
        """متن را برای وجود Flag بررسی می‌کند. اگر Candidate جدیدی پیدا شود True برمی‌گرداند."""
        found_new = False

        for flag in self._extract(text):
            if flag in self.seen:
                continue

            self.seen.add(flag)
            found_new = True

            base_score = score_text(text)
            # اگر با prefix دقیق مچ شده باشد امتیاز بیشتری می‌گیرد
            exact_bonus = 400 if self.specific_regex.match(flag) or self.specific_regex.search(flag) else 150

            self.candidates.append({
                "flag": flag,
                "path": list(path),
                "score": round(base_score + exact_bonus, 2),
            })

        return found_new

    def best_candidates(self, top_n=5):
        ranked = sorted(self.candidates, key=lambda c: c["score"], reverse=True)
        return ranked if top_n is None else ranked[:top_n]

    def strong_match(self, text: str) -> bool:
        """
        True یعنی متن تقریباً کامل همان Flag است (نه فقط شامل یک تکه‌ی آن).
        وقتی True برگردد، دیگر لازم نیست از این متن ادامه‌ی Decode گرفت
        (مثلاً دیگر نیازی نیست روی خودِ Flag پیدا‌شده، ROT13/Caesar اجرا شود) —
        این جلوی هدررفت محاسباتی بعد از پیدا شدن یک Flag تمیز را می‌گیرد.
        """
        if not text:
            return False

        m = self.specific_regex.search(text)
        if not m:
            return False

        span = m.end() - m.start()
        return span / max(len(text), 1) > 0.6
