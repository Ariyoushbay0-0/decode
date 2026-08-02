"""
search_profiles.py
-------------------
Fast Mode / Thorough Mode.

به‌جای هاردکد کردن beam_width و بقیه‌ی پارامترها تو main.py، اینجا دو تا
"پیش‌تنظیم" (Profile) آماده کردیم. کاربر انتخاب می‌کنه کدومو بخواد.

منطق انتخاب عددها (این بخش برای یادگیری مهم‌تر از خودِ عددهاست):

- beam_width: چند مسیر برتر در هر عمق نگه داشته بشه. عدد بزرگ‌تر = دقیق‌تر
  ولی کندتر، چون در هر لایه باید روی همه‌شون Decoderها رو اجرا کنی.

- max_depth: چند لایه Decode پشت‌سرهم امتحان بشه. اکثر چالش‌های CTF بیشتر
  از ۶-۷ لایه نیستن، ولی چون این هزینه‌ی زیادی نداره (فقط یه شرط توقفه)،
  برای Thorough زیاد نگهش داشتیم که چیزی از دست نره.

- max_total_nodes: سقف کلی گره‌هایی که کل الگوریتم در طول اجرا بررسی
  می‌کنه. این "ترمز دستی" واقعیه؛ حتی اگه beam_width بزرگ باشه، این عدد
  جلوی اجرای بی‌نهایت رو می‌گیره.

- adaptive_growth: وقتی یک عمق هیچ Flag جدیدی پیدا نکنه، beam_width چقدر
  موقتاً بزرگ‌تر بشه (fallback شبیه BFS). در Fast Mode این fallback رو
  محدودتر نگه داشتیم چون هدف سرعت اولویت داره.

خودِ اعداد قطعی نیستن - اگه یه چالش خاص داری که جواب نمیده، اول Thorough
رو امتحان کن، بعد اگه بازم طول کشید max_total_nodes رو دستی بالاتر ببر.
"""

SEARCH_PROFILES = {
    "fast": dict(
        beam_width=15,
        max_depth=12,
        max_total_nodes=4000,
        adaptive_growth=10,
        max_beam_width=120,
    ),
    "thorough": dict(
        beam_width=40,
        max_depth=20,
        max_total_nodes=20000,
        adaptive_growth=25,
        max_beam_width=400,
    ),
}

DEFAULT_PROFILE = "thorough"


def get_profile(name: str) -> dict:
    """اگه اسم نامعتبر بود، به‌جای Exception دادن، پیش‌فرض امن (thorough) برمی‌گردونیم."""
    return SEARCH_PROFILES.get(name.strip().lower(), SEARCH_PROFILES[DEFAULT_PROFILE])


def resolve_profile_name(name: str) -> str:
    """اسم نرمال‌شده‌ی Profile برای نمایش - اگه نامعتبر بود، همون DEFAULT_PROFILE برگردانده می‌شود."""
    key = name.strip().lower()
    return key if key in SEARCH_PROFILES else DEFAULT_PROFILE
