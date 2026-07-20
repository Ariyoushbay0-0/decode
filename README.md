# Auto Flag Decoder 🔍

یک ابزار خودکار برای CTF که تلاش می‌کند فلگ‌های چندلایه Encode شده را پیدا کند.

این ابزار متن ورودی را دریافت می‌کند، چندین روش Decode را به‌صورت خودکار امتحان می‌کند و با استفاده از الگوی فلگ، نتیجه نهایی را پیدا می‌کند.

---

## ✨ Features

* 🔹 پشتیبانی از Decode چندمرحله‌ای (Nested Encoding)
* 🔹 جستجوی خودکار با الگوریتم BFS
* 🔹 نمایش مسیر Decode تا رسیدن به فلگ
* 🔹 جلوگیری از حلقه‌های تکراری با سیستم `visited`
* 🔹 محدود کردن عمق جستجو برای جلوگیری از مصرف زیاد منابع
* 🔹 پشتیبانی از چند نوع Encoding:

  * Base64
  * Hex
  * URL Encoding
  * ROT1-25

---

## ⚙️ How It Works

روند کار برنامه:

```
Encoded Text
      |
      v
+-------------+
|  Decoder 1  |
+-------------+
      |
      v
+-------------+
|  Decoder 2  |
+-------------+
      |
      v
 Flag Found!
```

برنامه تمام مسیرهای احتمالی Decode را بررسی می‌کند.

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
 picoCTF{flag}
```

---
## 🧠 Algorithm

این پروژه از BFS استفاده می‌کند.

هر مرحله:

1. یک مقدار از Queue برداشته می‌شود.
2. تمام Decoderها روی آن تست می‌شوند.
3. خروجی‌های جدید وارد Queue می‌شوند.
4. بعد از هر Decode، الگوی فلگ بررسی می‌شود.

---

## 🔮 Future Plans

ویژگی‌هایی که در نسخه‌های بعد اضافه خواهند شد:

* [ ] Caesar Cipher brute force
* [ ] Single Byte XOR brute force
* [ ] Base32 Support
* [ ] Base58 Support
* [ ] Gzip / Zlib Detection
* [ ] Magic Header Analysis
* [ ] Entropy Based Scoring
* [ ] Custom Regex Flag Format
* [ ] File Input Support

---
