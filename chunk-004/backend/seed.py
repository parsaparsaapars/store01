import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()
from apps.inventory.models import Warehouse
from apps.products.models import Product, Category, Brand, Unit
from django.contrib.auth import get_user_model

# Warehouse
wh, _ = Warehouse.objects.get_or_create(name='انبار اصلی', defaults={'is_active': True})
print('warehouse', wh.id)

# Category/Brand/Unit defaults
cat, _ = Category.objects.get_or_create(name='عمومی')
brand, _ = Brand.objects.get_or_create(name='برند نمونه')
unit, _ = Unit.objects.get_or_create(name='عدد')

products = [
 ('دانه قهوه اسپرسو', '۶۲۶۰۱۲۹۹', 385000),
 ('روغن زیتون فرابکر', '۶۲۶۰۴۵۲۱', 490000),
 ('عسل طبیعی گون', '۶۲۶۰۷۸۱۴', 240000),
 ('مایع دستشویی لوکس', '۶۲۶۰۳۳۹۰', 65000),
 ('مخلوط مغز آجیل اعلا', '۶۲۶۰۹۰۱۱', 430000),
 ('چای سیاه بهاره گیلان', '۶۲۶۰۸۸۲۰', 195000),
]
for name, barcode, price in products:
    p, created = Product.objects.get_or_create(barcode=barcode, defaults={'name': name, 'sku': barcode, 'category': cat, 'brand': brand, 'unit': unit, 'sale_price': price, 'is_active': True})
    print('product', p.id, p.name, 'created' if created else 'exists')
print('done')
PYEOF