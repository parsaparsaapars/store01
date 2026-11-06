# راهنمای سریع سامانه (برای AI/توسعه‌دهنده)

این فایل خلاصهٔ «منبع حقیقت» برای درک سریع پروژه است. **قبل از اسکن کل مخزن، این فایل را بخوان.** فقط برای تغییرات عمیق، فایل مرجع همان بخش را باز کن.

## 1) چی هست این پروژه؟
- **نوع:** سامانه فروشگاهی/مدیریتی + **POS صندوق** (RTL، فارسی، تقویم/منطقه زمانی ایران).
- **Stack:** Django 5.2 + Django REST Framework + PostgreSQL + Redis + Celery + Nginx + Gunicorn + Whitenoise.
- **UI:** قالب‌های Django (SSR) با Tailwind CDN؛ صفحات UI در `backend/templates/ui/<slug>/code.html` رندر می‌شوند. شِل اصلی `backend/templates/base.html` شامل سایدبار/هدر/سبد خرید JS/checkout است.
- **Locale/تنظیمات پایه:** `fa-ir`, `Asia/Tehran`, کاربر سفارشی `accounts.User` (`backend/config/settings/base.py`).

## 2) ساختار مهم مخزن (فقط همین‌ها runtime اصلی‌اند)
| مسیر | نقش |
|---|---|
| `backend/config/` | تنظیمات `settings/{base,dev,prod}.py`, روت‌ها `urls.py`, `api_urls.py`, `wsgi/asgi` |
| `backend/apps/` | دامنه بیزنس (ماژول‌ها) |
| `backend/templates/base.html` | شِل UI + منطق سبد/پرداخت POS در JS |
| `backend/templates/ui/<slug>/code.html` | صفحه هر بخش UI |
| `backend/templates/core/home.html` | فهرست صفحات UI |
| `backend/apps/core/views.py` | نگاشت `/ui/<slug>/` و **تزریق context داده واقعی** برای هر صفحه |
| `backend/requirements.txt`, `backend/Dockerfile`, `backend/manage.py` | وابستگی/بیلد/اجرای جنگو |
| `docker-compose.yml` | prod-like: `db, redis, web, celery, celery-beat, nginx` |
| `docker-compose.dev.yml` | dev: `db, redis, web, celery, nginx` (بدون beat)، runserver |
| `nginx/nginx.conf` | proxy به `web:8000`، سرو `/static/` و `/media/` |
| `.env` | مقادیر محیطی (در compose DB/Celery override می‌شوند) |
| `ui/` | دارایی/طراحی UI (مرجع طراحی)؛ رندر واقعی از `backend/templates/ui` است |
| `backend/seed.py`, `seed_data.py` | داده نمونه اولیه |

**مهم:** در ریشه تعداد زیادی فایل موقتی/وصله (`fix_*.py`, `check*.py`, `replace*.py`, `temp_*.html`, `*.txt` snippet) وجود دارد. این‌ها ابزار اصلاح دستی‌اند؛ برای فهم/تغییر رفتار سامانه مبنا قرار نده مگر صراحتاً خواسته شود.

## 3) اجرا و محیط
```powershell
# Dev
docker compose -f docker-compose.dev.yml up --build
# Prod-like
docker compose -f docker-compose.yml up --build
```
- Dev: وب روی `:8000`، nginx روی `:8080`، Postgres host `:5433`، settings `config.settings.dev`.
- Prod compose: `migrate` + `gunicorn` (`--workers 3`)، nginx روی `:80`، settings `config.settings.prod`.
- DB پیش‌فرض dev می‌تواند SQLite باشد اگر `DATABASE_URL` ست نشود (`backend/config/settings/dev.py`)؛ در compose معمولاً Postgres است.

## 4) روتینگ (نقشه مسیرها)
مرجع: `backend/config/urls.py`
- `admin/`، `accounts/`، `products/`، `inventory/`، `sales/`، `purchases/`، `customers/`، `finance/`، `reports/`، `notifications/`، `settings/`، `search/`، `api/`، و `/` → `core`.
- API تجمیعی: `backend/config/api_urls.py` → `accounts, customers, products, search, sales, inventory` تحت `/api/...`
- UI صفحات: `GET /ui/<slug>/` → `core.views.page` → `templates/ui/<slug>/code.html` (`backend/apps/core/urls.py`).
- سلامت سیستم: `GET /api/status/` (DB/Redis/version/store/time) در `core.views.system_status`.

## 5) ماژول‌ها و مدل‌های کلیدی
پایه مشترک: `core.models.TimeStampedModel(created_at, updated_at)`.

| app | مدل/مسئولیت کلیدی | فایل مرجع |
|---|---|---|
| `accounts` | `User(AbstractUser, phone/role/branch)`, `Role(permissions JSON)`, `AuditLog`; لاگین → هدایت به POS؛ ریست رمز → اعلان امنیتی | `apps/accounts/models.py`, `views.py`, `urls.py` |
| `products` | `Category` درختی، `Brand`, `Unit`, `Product` (`sku` یکتا، `barcode` ایندکس، قیمت/مالیات/حداقل موجودی/تصویر/فعال)، `PriceList`, `Discount` | `apps/products/models.py` |
| `inventory` | `Warehouse`; `Stock` یکتا `(product,warehouse)` با `quantity/reserved/available`; `StockMovement` (`in/out/transfer/adjustment/return`); `StockTransfer(+Item)` | `apps/inventory/models.py` |
| `sales` | `Invoice/Item/Payment`, `SalesReturn/Item`؛ **checkout POS** اتمیک | `apps/sales/models.py`, `views.py`, `api_urls.py` |
| `customers` | `Customer` (اعتبار/امتیاز وفاداری/فعال)، `CustomerPayment` | `apps/customers/models.py` |
| `purchases` | `Supplier`, `PurchaseOrder/Item/Receipt` | `apps/purchases/models.py` |
| `finance` | `Cashbox`, `BankAccount`, `FinanceTransaction`, `Expense`, `Receivable`, `Payable` | `apps/finance/models.py` |
| `settings_app` | `StoreSettings` (نام فروشگاه، لوگو، ارز، نرخ مالیات، پیشوند فاکتور، شعبه، تلفن، نسخه) | `apps/settings_app/models.py` |
| `notifications` | `Notification` (priority/category/read/link/user) | `apps/notifications/models.py` |
| `search` | API جستجوی سراسری محصولات/مشتریان/فاکتورها/تأمین‌کنندگان | `apps/search/views.py` |
| `reports` | endpoint پایه/گزارش‌ها (کم‌عمق‌تر؛ در صورت نیاز همان app را بخوان) | `apps/reports/views.py` |

## 6) جریان حیاتی: فروش POS
مرجع اصلی: `backend/apps/sales/views.py` → `pos_checkout` (`POST /api/sales/pos-checkout/`, auth لازم).
1. اعتبارسنجی سبد/اقلام/محصول؛ انبار از ورودی یا اولین انبار فعال.
2. محاسبه مبالغ: تخفیف/مالیات درصدی یا مبلغی، حمل، جمع کل.
3. شماره فاکتور یکتا با `StoreSettings.invoice_prefix`.
4. **کنترل موجودی قبل از ثبت**: اگر `qty > available` → خطا (جلوگیری از oversell).
5. در `transaction.atomic`: ساخت `Invoice(status=final)` + `InvoiceItem` + `InvoicePayment`؛ سپس برای هر قلم **کسر `Stock.quantity`** و ثبت `StockMovement(type=out, reference=invoice_no, note="فروش POS")`.
6. خروجی JSON: `ok, invoice_id, invoice_no, total, payment_status`.

سمت UI: `base.html` سبد را در `localStorage (posCart)` نگه می‌دارد، product id را resolve می‌کند، و به `/api/sales/pos-checkout/` با `X-CSRFToken` POST می‌زند. داده اولیه POS (انبار/محصول/موجودی/دسته/مشتری/تنظیمات) از `core.views.page` برای slug `pos` تزریق می‌شود.

## 7) الگوی UI داده‌محور
- `core.views.page(slug)` فقط template را رندر نمی‌کند؛ برای slugهای مهم **query و context** می‌سازد (مثلاً `dashboard, pos, product-list/form, inventory/stock/warehouse, purchase/supplier, customer, finance/cashbox, sales-report/return, pricing-discounts, profit-loss-report, settings, user-management, global-search`).
- اگر رفتار/داده یک صفحه UI اشتباه است: اول `backend/apps/core/views.py` بخش همان `slug`، بعد `templates/ui/<slug>/code.html`، سپس model/view/app مرتبط.

## 8) احراز هویت و دسترسی
- ورود: `/accounts/login/` (`accounts.views.login_view`)؛ موفق → `/ui/pos/`.
- APIها عمدتاً `IsAuthenticated`/`IsAuthenticatedOrReadOnly` (DRF). `pos_checkout` احراز هویت می‌خواهد.
- ریست رمز: ثبت ticket و ایجاد `Notification` بحرانی برای مدیران (بدون افشای وجود کاربر).

## 9) نکات فنی/ریسک‌های شناخته‌شده
- **Encoding/Farsi mojibake:** برخی فایل‌ها/متون ممکن است نمایش خراب داشته باشند؛ تغییر متن فارسی را با احتیاط و حفظ encoding صحیح انجام بده.
- **فایل‌های موقتی ریشه:** `fix/check/inject/replace/temp` منبع حقیقت نیستند.
- **DB:** `backend/db.sqlite3` وجود دارد ولی معماری هدف compose معمولاً Postgres+Redis است؛ با settings/env هماهنگ کار کن.
- **امنیت:** `prod` شامل SSL redirect/HSTS/secure cookies است؛ مقادیر `.env` نمونه باید در محیط واقعی امن شوند.

## 10) چک‌لیست سریع برای تغییرات
1. تغییر مدل → `apps/<domain>/models.py` (+ migration) و اثر روی serializer/view/context UI.
2. تغییر POS/فاکتور/موجودی → `apps/sales/views.py`, `sales/models.py`, `inventory/models.py`, `templates/base.html` (JS سبد/checkout).
3. تغییر داده صفحه UI → `core/views.py` (بخش slug) + `templates/ui/<slug>/code.html`.
4. تغییر API → `apps/<domain>/api_urls.py|views.py|serializers.py` و ثبت در `config/api_urls.py` در صورت نیاز.
5. تغییر تنظیمات/زیرساخت → `config/settings/*`, `docker-compose*.yml`, `nginx/nginx.conf`, `.env`.

## 11) قواعد پیشنهادی برای AI
- ابتدا این فایل و سپس **فقط فایل مرجع بخش مرتبط** را بخوان؛ از grep/scan سراسری پرهیز کن مگر لازم شود.
- از وصله‌اسکریپت‌های ریشه تقلید نکن؛ تغییرات را در `backend/apps`, `backend/templates`, `backend/config` اعمال کن.
- منطق مالی/موجودی را بدون تراکنش و بدون کنترل موجودی تغییر نده.
- برای هر تغییر UI داده‌محور، هم context (`core/views.py`) هم template را بررسی کن.
