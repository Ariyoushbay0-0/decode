# Auto Flag Decoder 🔍

یک ابزار خودکار برای CTF که تلاش می‌کند فلگ‌های چندلایه Encode شده را پیدا کند.

این ابزار متن ورودی را دریافت می‌کند، با یک موتور جستجوی هوشمند (**Beam Search + A\***) چندین مسیر Decode را همزمان امتحان می‌کند، هر خروجی را با یک **Scoring Engine** امتیازدهی می‌کند و در نهایت تمام Candidateهای Flag را رتبه‌بندی‌شده نمایش می‌دهد.

---

## ✨ Features

🔹 پشتیبانی از Decode چندمرحله‌ای (Nested Encoding)
🔹 جستجوی هوشمند با **Beam Search + A\*** (به‌جای BFS ساده)
🔹 **Scoring Engine** برای امتیازدهی به هر خروجی Decode (printable ratio، خوانایی، Entropy، الگوی Flag)
🔹 **Decoder Weight System** — هر Decoder هزینه‌ی خودش را دارد تا مسیرهای منطقی زودتر بررسی شوند
🔹 **Flag Validator** — به‌جای برگرداندن اولین Flag، همه‌ی Candidateها را پیدا و رتبه‌بندی می‌کند
🔹 نمایش کامل مسیر Decode + امتیاز نهایی تا رسیدن به هر Flag
🔹 جلوگیری از حلقه‌های تکراری و پردازش تکراری با سیستم `visited`
🔹 Adaptive Beam: اگر یک عمق نتیجه نداد، عرض جستجو موقتاً افزایش می‌یابد تا احتمال از‌دست‌رفتن Flag کم شود
🔹 محدود کردن عمق و تعداد گره‌های جستجو برای جلوگیری از مصرف زیاد منابع
🔹 گزارش زمان اجرا و تعداد گره‌های بررسی‌شده در پایان
🔹 معماری کاملاً ماژولار (Decoder / Scoring / Search / Validator جدا از هم)
🔹 پشتیبانی از چندین نوع Encoding:

### Encoding / Decoding Methods

- Base64
- Base64 URL-safe
- Base32
- Base85
- Hex
- Binary ASCII
- Decimal ASCII
- Octal ASCII
- URL Encoding
- Unicode Escape
- HTML Entity
- Quoted Printable
- Reverse Text
- ROT13
- Caesar Cipher (ROT1-25)

---

# ⚙️ How It Works

روند کار برنامه:

```
Encoded Text
      |
      v
+-------------------+
|  Beam Search Node  |  <-- امتیاز = Cost(Decoderها) - Score(متن)
+-------------------+
      |
      v
  همه‌ی Decoderها روی متن تست می‌شوند
      |
      v
  فقط بهترین N مسیر نگه داشته می‌شود (Beam Width)
      |
      v
  هر خروجی توسط Flag Validator چک می‌شود
      |
      v
 همه‌ی Flagهای پیدا‌شده جمع‌آوری و رتبه‌بندی می‌شوند
```

برنامه به‌جای بررسی *همه‌ی* مسیرهای احتمالی (مثل BFS)، در هر عمق فقط بهترین مسیرها را با Beam Search + A* دنبال می‌کند، اما اگر مسیر امیدبخشی پیدا نشود، عرض جستجو را موقتاً افزایش می‌دهد تا چیزی از دست نرود.

مثال:

```
Input
 |
 Base64
 |
 Hex
 |
 ROT13
 |
 unlim{flag}
```

---

# 🧠 Algorithm

این پروژه از **Beam Search + A\*** استفاده می‌کند (به‌جای BFS ساده‌ی نسخه‌ی اول).

در هر مرحله:

1. یک لایه از بهترین Nodeهای موجود برداشته می‌شود (نه فقط یکی، نه همه).
2. تمام Decoderها روی هر Node تست می‌شوند (Caesar/ROT13 فقط روی متن‌های معنادار اجرا می‌شوند تا وقت روی گارباژ باینری تلف نشود).
3. برای هر خروجی جدید:
   - `g(n)` = هزینه‌ی تجمعی مسیر (از **Decoder Weight System**)
   - `h(n)` = امتیاز متن (از **Scoring Engine**: printable ratio, خوانایی, Entropy, الگوی Flag, ...)
   - `f(n) = g(n) - h(n)` تعیین‌کننده‌ی اولویت است.
4. فقط `beam_width` مسیر برتر برای لایه‌ی بعد نگه داشته می‌شوند؛ اگر لایه‌ای هیچ Flag جدیدی نداد، این عرض موقتاً بزرگ‌تر می‌شود (**Adaptive Beam**).
5. بعد از هر Decode، **Flag Validator** متن را برای همه‌ی الگوهای ممکن Flag بررسی می‌کند (نه فقط اولین match).
6. وقتی متنی خودش تقریباً کامل یک Flag معتبر باشد، دیگر از آن ادامه داده نمی‌شود (جلوگیری از هدررفت محاسباتی).
7. در پایان، همه‌ی Candidateهای Flag بر اساس امتیاز نهایی رتبه‌بندی و نمایش داده می‌شوند.

---

# 🗂️ Project Structure

```
auto_flag_decoder/
├── main.py             # نقطه‌ی ورود: ورودی می‌گیرد، موتور را اجرا می‌کند، نتیجه را چاپ می‌کند
├── decoders.py          # همه‌ی Decoderها (Base64, Hex, ROT, Caesar, ...)
├── decoder_weights.py   # Decoder Weight System — هزینه‌ی هر Decoder برای g(n)
├── scoring.py           # Scoring Engine — امتیازدهی h(n) به هر خروجی
├── flag_validator.py    # تشخیص، اعتبارسنجی و رتبه‌بندی Candidateهای Flag
└── search_engine.py     # موتور Beam Search + A*
```

هیچ فایلی به فایل دیگری وابستگی چرخه‌ای ندارد؛ هرکدام را می‌توان جدا تست یا جایگزین کرد.

---

# 🚀 Installation

Clone repository:

```bash
git clone https://github.com/Ariyoushbay0-0/decode.git
```

ورود به پوشه:

```bash
cd decode
```

نصب وابستگی‌ها (فعلاً هیچ پکیج خارجی لازم نیست، فقط کتابخانه‌ی استاندارد پایتون):

```bash
pip install -r requirements.txt
```

اجرای برنامه:

```bash
python3 main.py
```

> نیازمند Python 3.8 یا بالاتر.

---

# 📝 Example

Input:

```
Flag format:
unlim{}
Encoded text:
dW5saW17ZGVjb2RlfQ
```

Output:

```
(زمان اجرا: 0.041s | گره‌های بررسی‌شده: 187)

================ RESULTS (1 flag یافت شد) ================

Rank 1 | Score: 1387.6
Path:
  ↓ Base64
Flag:
  unlim{decode}
```

---

# 🔮 Future Plans

ویژگی‌هایی که در نسخه‌های بعد اضافه خواهند شد:

- Single Byte XOR brute force
- Multi Byte XOR Support
- Gzip / Zlib Detection
- Magic Header Analysis
- File Input Support
- Automatic Flag Format Detection
- Custom Regex Flag Format
- Archive Analysis (ZIP, TAR, 7z)
- Image Steganography Helpers
- Fast Mode / Thorough Mode toggle (Beam Width و سقف گره‌ها از پیش‌تنظیم‌شده)
- Confidence Gap Warning (هشدار وقتی امتیاز Rank 1 و Rank 2 خیلی نزدیک‌اند و احتمال False Positive هست)

> ✅ Entropy Based Scoring و چند‌Candidate بودن Flag Detection در این نسخه پیاده‌سازی شدند.

---

# ⚠️ Note

این ابزار برای اهداف آموزشی، CTF و تحلیل داده‌های رمزگذاری‌شده طراحی شده است.
در چالش‌های CTF، سرعت و دقت ابزار به نوع Encoding، عمق Decode و محدودیت منابع (`max_depth`, `beam_width`, `max_total_nodes` در `main.py`) بستگی دارد.
