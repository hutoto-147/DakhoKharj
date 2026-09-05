# DakhlKharj — Safe MainActivity Refactor Pack

این بسته برای **گام اول اصلاح ساختار MainActivity** ساخته شده است.

هدف این مرحله فقط جدا کردن مسئولیت‌های اصلی است:

```text
MainActivity
    ↓
ui/app/LedgerApp
    ↓
ui/app/MainScaffold
    ↓
LegacyScreens
    ↓
Existing Repository / DB
```

در این مرحله عمداً UI جدید Word و افکت‌های libraries.dev اعمال نمی‌شوند. اول باید ساختار جدید Build شود.

## فایل‌های بسته

- `refactor_templates/MainActivity.kt`
- `refactor_templates/LedgerApp.kt`
- `refactor_templates/MainScaffold.kt`
- `tools/apply_main_refactor.py`

اسکریپت، `LegacyScreens.kt` را از **MainActivity.kt فعلی خود پروژه** تولید می‌کند؛ بنابراین لازم نیست فایل بزرگ Main را دستی Cut/Paste کنید.

## روش پیشنهادی: Branch جدید در همان Repository

Repository جدید لازم نیست. branch جدید امن‌تر و راحت‌تر برای مقایسه/rollback است.

از root پروژه:

```bash
git switch main
git pull
git switch -c refactor/main-ui-structure
```

بعد محتویات این ZIP را در root repository کپی کنید.

ساختار باید این‌طور دیده شود:

```text
DakhoKharj/
├── app/
├── tools/
│   └── apply_main_refactor.py
├── refactor_templates/
│   ├── MainActivity.kt
│   ├── LedgerApp.kt
│   └── MainScaffold.kt
└── ...
```

سپس:

```bash
python3 tools/apply_main_refactor.py
```

اسکریپت قبل از جایگزینی Main یک backup متنی می‌سازد:

```text
refactor_backup/MainActivity.before_ui_refactor.kt.txt
```

## Build و Test

اول:

```bash
./gradlew testDebugUnitTest
```

بعد:

```bash
./gradlew assembleDebug
```

تا وقتی هر دو سبز نشده‌اند branch را با `main` merge نکنید.

## Commit پیشنهادی

اگر Build موفق بود:

```bash
git status
git add app/src/main/java/com/example/kharjyar/MainActivity.kt
git add app/src/main/java/com/example/kharjyar/LegacyScreens.kt
git add app/src/main/java/com/example/kharjyar/ui/app/LedgerApp.kt
git add app/src/main/java/com/example/kharjyar/ui/app/MainScaffold.kt
git add tools/apply_main_refactor.py
git commit -m "refactor: split app root and main scaffold from MainActivity"
git push -u origin refactor/main-ui-structure
```

`refactor_backup/` و `refactor_templates/` لازم نیست وارد commit اصلی شوند؛ templateها فقط برای اجرای اسکریپت‌اند. اگر می‌خواهید repository تمیز بماند، بعد از موفقیت Build حذفشان کنید.

## اگر Build شکست خورد

هیچ تغییری روی `main` انجام نشده است. ساده‌ترین بازگشت:

```bash
git switch main
```

یا اگر می‌خواهید branch آزمایشی را کامل حذف کنید:

```bash
git switch main
git branch -D refactor/main-ui-structure
```

## اگر فقط از GitHub Web استفاده می‌کنید

روش بهتر این است که در GitHub:

1. روی branch selector کلیک کنید.
2. branch جدید با نام `refactor/main-ui-structure` بسازید.
3. فایل‌های بسته را روی همان branch Upload کنید.
4. اسکریپت را در Codespaces یا clone محلی اجرا کنید.
5. Pull Request از branch جدید به `main` بسازید.
6. فقط بعد از سبز شدن CI آن را Merge کنید.

## خط قرمزهای این مرحله

این refactor نباید این فایل‌ها/رفتارها را تغییر دهد:

- database schema
- `LedgerRepository` behavior
- `LedgerDb.kt`
- transaction save/edit/delete semantics
- debt/loan behavior
- recurring transactions
- reminder scheduling
- PIN / biometric behavior
- import/export/backup logic

بعد از Build موفق، گام بعدی انتقال `LegacyScreens.kt` به `ui/screens` و `ui/components` و سپس redesign مطابق سند Word است.
