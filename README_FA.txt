روش ساده اعمال روی GitHub بدون Codespaces

1) ابتدا از ریپوی اصلی KharjYar یک ریپوی جدید بساز (Template/Import/Fork خصوصی یا عمومی).
2) فایل apply_kharjyar_update.py را در ریشه ریپوی جدید آپلود کن.
3) فایل .github/workflows/apply-kharjyar-update.yml را با همین مسیر داخل ریپو قرار بده.
4) هر دو را Commit کن.
5) وارد تب Actions شو.
6) Workflow با نام Apply KharjYar Update را باز کن.
7) Run workflow را بزن.
8) بعد از سبز شدن اجرا، سورس اصلی پروژه خودکار تغییر می‌کند و یک Commit جدید ساخته می‌شود.

نکته: این Workflow را فقط یک‌بار روی نسخه فعلی ریپوی اصلی اجرا کن. اگر قبلاً تغییرات اعمال شده باشند، دوباره اجرا نکن.
