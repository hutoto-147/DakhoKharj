# آپدیت خرج‌یار به نسخه 0.2 از طریق GitHub

برای Repository فعلی لازم نیست همه چیز را از اول بسازید.

## فایل‌هایی که باید جایگزین شوند

از بسته Update این موارد را آپلود کنید:

- `app/src/main/java/com/example/kharjyar/MainActivity.kt`
- `app/src/main/java/com/example/kharjyar/LedgerDb.kt`
- `app/src/main/java/com/example/kharjyar/Models.kt`
- `app/src/main/java/com/example/kharjyar/PersianUtils.kt`
- `app/build.gradle.kts`
- `app/kharjyar-test.keystore`

ساده‌ترین روش در GitHub: از صفحه اصلی Repository روی `Add file` سپس `Upload files` بزنید و پوشه `app` داخل بسته Update را Drag & Drop کنید. GitHub فایل‌های هم‌نام را به‌روزرسانی می‌کند.

بعد `Commit changes` را بزنید. Workflow ساخت APK خودکار شروع می‌شود.

## نکته مهم درباره نصب نسخه 0.2

نسخه 0.2 از یک کلید تست ثابت استفاده می‌کند تا APKهای بعدی بتوانند روی همین نسخه نصب و آپدیت شوند. نسخه 0.1 قبلی با کلید موقت GitHub Runner ساخته شده بود؛ بنابراین برای نصب 0.2 احتمالاً لازم است نسخه 0.1 را یک بار Uninstall کنید. از نسخه 0.2 به بعد، تا وقتی همین keystore حفظ شود، آپدیت‌های تستی روی هم نصب می‌شوند.

این کلید فقط برای تست شخصی است و برای انتشار نهایی در Google Play استفاده نمی‌شود.
