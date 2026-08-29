# گرفتن APK بدون Android Studio

این پروژه برای GitHub Actions آماده شده است و نیازی به Android Studio روی کامپیوتر شما ندارد.

## روش سریع

1. وارد GitHub شوید و یک Repository جدید بسازید.
2. محتویات پوشه `KharjYarAndroid` را داخل Repository آپلود کنید. مهم است پوشه `.github` هم آپلود شود.
3. وارد تب **Actions** شوید.
4. Workflow با نام **Build Android APK** را باز کنید.
5. اگر بیلد خودکار شروع نشده بود، **Run workflow** را بزنید.
6. بعد از موفق شدن بیلد، همان صفحه Workflow را باز کنید.
7. پایین صفحه، در بخش **Artifacts**، فایل **KharjYar-debug-apk** را دانلود کنید.
8. فایل ZIP دانلودشده را باز کنید؛ داخل آن `app-debug.apk` است.
9. APK را به گوشی منتقل و نصب کنید. ممکن است Android برای نصب فایل خارج از Play Store از شما اجازه «Install unknown apps» بخواهد.

## نکته

این APK نسخه Debug برای تست شخصی است. برای انتشار عمومی در Google Play باید نسخه Release امضاشده ساخته شود.
