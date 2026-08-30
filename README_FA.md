# V8 — Dashboard Cards

این نسخه فقط ظاهر کارت‌های صفحه اول را اصلاح می‌کند.

تغییرها:
- حذف متن «نمایش جزئیات» از کارت‌های درآمد، هزینه و مانده
- حذف «جزئیات» از کارت‌های بدهی و قرض
- اضافه شدن فلش کوچک روی عنوان برای نشان دادن قابل‌کلیک بودن
- کل کارت همچنان قابل لمس است و همان صفحه مقایسه قبلی را باز می‌کند
- بکاپ/بازیابی دست‌نخورده می‌ماند
- Fragment 1.9.0 که مشکل requestCode را حل کرد حفظ می‌شود
- versionCode = 8 / versionName = 1.0.8

آپلود:
1) apply_v6_backup_fix.py -> ریشه ریپو
2) apply_v8_dashboard_cards.py -> ریشه ریپو
3) .github/workflows/build-v8-dashboard-cards.yml -> پوشه workflows

بعد:
Actions -> Build V8 Dashboard Cards APK -> Run workflow

Artifact:
DakhlKharj-V8-Dashboard-Cards-APK

V7 نصب‌شده روی گوشی را حذف نکن؛ V8 باید روی آن Update شود.
