# مراحل انتشار دخل و خرج 1.0.0

## مرحله فعلی

این بسته سورس نسخه عمومی را آماده می‌کند، اما هنوز نباید Release عمومی ساخته شود.

### تغییرات مهم

- Application ID جدید: `io.github.hutoto147.dakhlokharj`
- Version: `1.0.0` / versionCode `1`
- حذف کلید تستی از سورس عمومی
- حذف READ_SMS / RECEIVE_SMS و SMS Receiver از نسخه عمومی
- Notification Access با disclosure و consent داخل برنامه
- Privacy Policy برای GitHub Pages
- Release signing فقط از GitHub Secrets

## پس از Upload

1. فایل `app/kharjyar-test.keystore` را در GitHub از branch انتشار حذف کنید.
2. مطمئن شوید `.gitignore` اضافه شده است.
3. Actions را اجرا کنید و Debug Build باید سبز شود.
4. هنوز Workflow AAB را اجرا نکنید؛ ابتدا Upload Key امن می‌سازیم و Secrets را تنظیم می‌کنیم.
5. پس از آن AAB را می‌سازیم و وارد Play Console Internal/Closed Testing می‌شویم.

## پاکسازی Repository قبل از Merge

در branch انتشار این فایل‌ها را اگر هنوز وجود دارند حذف کنید:

- `app/kharjyar-test.keystore`
- `MainActivity (1).kt`
- `PersianUtils (1).kt`

فایل‌های `.github/workflows/build-apk.yml` و `.github/workflows/release-v1.yml` باید دقیقاً از این بسته جایگزین شوند.
