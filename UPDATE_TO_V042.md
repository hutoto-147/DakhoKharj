# Update v0.4.2 / 1.1.0-beta2

این بسته برای نصب به‌صورت Update روی نسخه beta1 آماده شده است.

## تغییرات
- حذف توضیح اضافه زیر انتخاب رنگ و فونت.
- ذخیره مستقیم Backup، Excel و PDF در `Downloads/DakhlKharj` روی Android 10 به بالا.
- مسیر بدون نیاز به مجوز Storage برای Androidهای جدید.
- بررسی واقعی باز شدن OutputStream؛ موفقیت کاذب دیگر نمایش داده نمی‌شود.
- بازیابی با File Picker ساده‌تر (`GetContent`).
- ساخت بکاپ ایمنی داخلی قبل از هر Restore.
- عملیات فایل روی `Dispatchers.IO` انجام می‌شود.
- `versionCode = 6` و `versionName = 1.1.0-beta2`.
- `applicationId` و کلید signing قبلی حفظ شده‌اند تا Update و اطلاعات قبلی حفظ شود.

## فایل‌های اصلی تغییرکرده
- `app/src/main/java/com/example/kharjyar/MainActivity.kt`
- `app/src/main/java/com/example/kharjyar/FileTransferSupport.kt` (جدید)
- `app/build.gradle.kts`

لوگو در این نسخه عمداً تغییر نکرده و برای نسخه بعدی از صفر طراحی خواهد شد.
