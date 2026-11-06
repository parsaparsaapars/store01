# organized - کپی دسته‌بندی‌شده سامانه فروشگاه

**قانون اعمال‌شده:** هر پوشه و کل زیردرخت آن (همه فایل‌ها + پوشه‌های تو در تو) **<= 100** آیتم.
- پروژه اصلی تغییر نکرده.
- فایل‌های موقتی/غیرضروری کپی نشده‌اند (`fix/check/replace/temp`, `.env`, `db.sqlite3`, `staticfiles`, `.playwright-mcp`, کش، وصله‌ها).

## وضعیت بررسی
- chunkها: 13
- تخلف سقف 100: 0

## ساختار
- `docs/` — `SYSTEM_GUIDE.md` و مرجع‌ها.
- `chunk-NNN/_CONTENTS.txt` — حوزه‌های داخل chunk.
- `chunk-NNN/<مسیر اصلی>/...` — مسیر نسبی اصلی حفظ شده (مثلاً `backend/apps/sales/views.py`, `backend/config/settings/base.py`, `backend/templates/base.html`, `backend/templates/ui/pos/code.html`, `nginx/nginx.conf`, `docker-compose*.yml`, `ui/...`).
- `MANIFEST.txt` — نگاشت فایل‌ها به chunk.

## برای AI
برای فهم سریع: اول `docs/SYSTEM_GUIDE.md`، بعد `_CONTENTS.txt` هر chunk مرتبط. برای جزئیات کد، همان مسیر اصلی داخل chunk را باز کن. مرجع اجرای واقعی، پروژه اصلی است.
