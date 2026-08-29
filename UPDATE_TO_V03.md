# آپدیت Repository فعلی به خرج‌یار 0.3

اگر Repository قبلی را دارید، نیازی نیست از صفر پروژه بسازید.

1. فایل `KharjYar-v0.3-Update.zip` را Extract کنید.
2. وارد پوشه Extractشده شوید.
3. در GitHub، Repository خرج‌یار را باز کنید.
4. `Add file` → `Upload files` را بزنید.
5. پوشه `app` داخل بسته Update را Drag & Drop کنید.
6. صبر کنید همه فایل‌ها آپلود شوند و `Commit changes` را بزنید.
7. GitHub Actions خودکار Build جدید را شروع می‌کند.
8. اگر Build سبز شد، Artifact را دانلود کنید و `app-debug.apk` را نصب کنید.

## قبل از نصب

- اگر روی گوشی نسخه 0.2 نصب است: APK جدید باید به‌صورت Update روی آن نصب شود و دیتابیس با Migration حفظ شود.
- اگر هنوز نسخه 0.1 اولیه نصب است و داده مهم دارید: آن را Uninstall نکنید؛ به راهنمای `DATA_MIGRATION_V01.md` مراجعه کنید، چون نسخه 0.1 با کلید موقت دیگری امضا شده است.
