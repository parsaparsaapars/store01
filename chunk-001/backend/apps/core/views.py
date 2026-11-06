from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.db import connection
from django.db.models import Sum, Count, F, Q
from pathlib import Path
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json
from apps.products.models import Category, Product, Brand, Unit, PriceList, Discount

def home(request):
    base = Path(settings.BASE_DIR) / "templates" / "ui"
    slugs = []
    if base.exists():
        for d in sorted(base.iterdir()):
            if d.is_dir() and (d/"code.html").exists():
                name_file = d/"name.txt"
                name = name_file.read_text(encoding="utf-8").strip() if name_file.exists() else d.name
                slugs.append((d.name, name))
    return render(request, "core/home.html", {"pages": slugs})

def system_status(request):
    """وضعیت زندهٔ سیستم: DB، Redis و نسخهٔ سامانه — برای بج وضعیت در UI."""
    status = {"server": "ok", "db": "ok", "redis": "ok", "version": "", "time": ""}
    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        status["server"] = "error"
        status["db"] = "error"
    # Redis
    try:
        import redis as redis_lib
        url = getattr(settings, "CELERY_BROKER_URL", "redis://redis:6379/0")
        r = redis_lib.Redis.from_url(url, socket_connect_timeout=2, socket_timeout=2)
        r.ping()
    except Exception:
        status["redis"] = "error"
        if status["server"] == "ok":
            status["server"] = "degraded"
    # Store info
    try:
        from apps.settings_app.models import StoreSettings
        s = StoreSettings.objects.first()
        if s:
            status["version"] = s.system_version
            status["store_name"] = s.store_name
            status["branch_name"] = s.branch_name
    except Exception:
        pass
    status["time"] = timezone.now().strftime("%H:%M:%S")
    return JsonResponse(status)

def page(request, slug):
    tpl = f"ui/{slug}/code.html"
    context = {}
    if slug == "product-list":
        from apps.inventory.models import Stock, Warehouse, StockMovement
        # Support filtering by status: active, draft, all
        status_filter = request.GET.get('status', 'all')
        if status_filter == 'draft':
            all_products = Product.objects.filter(is_active=False)
        elif status_filter == 'all':
            all_products = Product.objects.all()
        else:
            all_products = Product.objects.filter(is_active=True)
        
        total_products = Product.objects.all().count()
        active_products = Product.objects.filter(is_active=True).count()
        draft_products = Product.objects.filter(is_active=False).count()
        # موجودی کل هر محصول (مجموع همهٔ انبارها)
        stock_total = {s["product"]: s["q"] for s in
                       Stock.objects.values("product").annotate(q=Sum("quantity"))}
        stock_reserved = {s["product"]: s["r"] for s in
                          Stock.objects.values("product").annotate(r=Sum("reserved"))}
        # وضعیت‌ها: کم‌موجودی/ناموجود نسبت به min_stock
        low_count, out_count = 0, 0
        for p in all_products:
            q = float(stock_total.get(p.id, 0))
            mn = float(p.min_stock or 0)
            if q <= 0:
                out_count += 1
            elif mn > 0 and q <= mn:
                low_count += 1
        context["pl_total_products"] = total_products
        context["pl_active_products"] = active_products
        context["pl_draft_products"] = draft_products
        context["pl_low_products"] = low_count
        context["pl_out_products"] = out_count
        context["pl_current_status"] = status_filter
        # لیست محصولات با موجودی واقعی
        products = (all_products.select_related("category", "brand", "unit")
                    .order_by("id"))
        pl_products = []
        for p in products:
            qty = float(stock_total.get(p.id, 0))
            reserved = float(stock_reserved.get(p.id, 0))
            mn = float(p.min_stock or 0)
            cost = float(p.cost_price or 0)
            sale = float(p.sale_price or 0)
            margin = round((sale - cost) / cost * 100, 1) if cost > 0 else None
            if qty <= 0:
                stock_state = "out"
            elif mn > 0 and qty <= mn:
                stock_state = "critical"
            else:
                stock_state = "in_stock"
            pl_products.append({
                "id": p.id, "name": p.name, "sku": p.sku, "barcode": p.barcode,
                "description": p.description or "", "category": p.category.name if p.category else "",
                "brand": p.brand.name if p.brand else "", "unit": p.unit.name if p.unit else "",
                "image_url": p.image.url if p.image else None,
                "qty": qty, "reserved": reserved, "available": qty - reserved, "min_stock": mn,
                "cost_price": cost, "sale_price": sale, "margin": margin,
                "is_active": p.is_active, "stock_state": stock_state,
            })
        context["pl_products"] = pl_products
        # فیلترها: دسته‌ها، انبارها، برندها
        context["pl_categories"] = list(Category.objects.filter(is_active=True).values_list("name", flat=True))
        context["pl_warehouses"] = list(Warehouse.objects.filter(is_active=True).values("id", "name"))
        context["pl_brands"] = list(Brand.objects.values_list("name", flat=True))
        context["pl_units"] = list(Unit.objects.values_list("name", flat=True))
        # آخرین به‌روزرسانی موجودی
        last_move = StockMovement.objects.order_by("-created_at").first()
        context["pl_last_stock_update"] = last_move.created_at if last_move else None
    if slug == "product-create":
        context["pf_categories"] = list(Category.objects.filter(is_active=True).values("id", "name"))
        context["pf_brands"] = list(Brand.objects.all().values("id", "name"))
        context["pf_units"] = list(Unit.objects.all().values("id", "name"))
    if slug == "product-form":
        from django.shortcuts import get_object_or_404
        context["pf_categories"] = list(Category.objects.filter(is_active=True).values("id", "name"))
        context["pf_brands"] = list(Brand.objects.all().values("id", "name"))
        context["pf_units"] = list(Unit.objects.all().values("id", "name"))
        pid = request.GET.get("id")
        if pid:
            p = get_object_or_404(Product, id=pid)
            context["pf_product"] = {
                "id": p.id, "name": p.name, "sku": p.sku, "barcode": p.barcode or "",
                "category_id": p.category_id, "brand_id": p.brand_id, "unit_id": p.unit_id,
            "cost_price": str(p.cost_price), "sale_price": str(p.sale_price),
            "tax_rate": str(p.tax_rate), "min_stock": str(p.min_stock),
            "description": p.description or "", "is_active": p.is_active,
            "image": p.image.url if p.image else "",
            }
    if slug == "inventory-dashboard":
        from apps.inventory.models import Warehouse, Stock, StockMovement
        warehouses = list(Warehouse.objects.filter(is_active=True).values("id", "name", "address", "manager"))
        total_warehouses = Warehouse.objects.filter(is_active=True).count()
        total_stock_qty = Stock.objects.aggregate(t=Sum("quantity"))["t"] or 0
        total_reserved = Stock.objects.aggregate(r=Sum("reserved"))["r"] or 0
        low_stock_items = Stock.objects.filter(quantity__lte=F("product__min_stock")).select_related("product", "warehouse")[:10]
        low_stock_count = Stock.objects.filter(quantity__lte=F("product__min_stock")).count()
        out_stock_count = Stock.objects.filter(quantity__lte=0).count()
        recent_moves = list(StockMovement.objects.select_related("product", "warehouse").order_by("-created_at")[:15].values(
            "id", "movement_type", "quantity", "reference", "note", "created_at",
            product_name=F("product__name"), warehouse_name=F("warehouse__name")
        ))
        inv_products = []
        for p in Product.objects.filter(is_active=True).select_related("category", "brand", "unit").order_by("-id")[:200]:
            stocks = Stock.objects.filter(product=p)
            total_qty = sum(float(s.quantity) for s in stocks)
            total_reserved_qty = sum(float(s.reserved) for s in stocks)
            available_qty = total_qty - total_reserved_qty
            first_stock = stocks.first()
            inv_products.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "barcode": p.barcode or "",
                "category_name": p.category.name if p.category else "",
                "brand_name": p.brand.name if p.brand else "",
                "unit_name": p.unit.name if p.unit else "",
                "category": p.category.name if p.category else "",
                "unit": p.unit.name if p.unit else "",
                "min_stock": float(p.min_stock),
                "total_qty": total_qty,
                "reserved_qty": total_reserved_qty,
                "available_qty": available_qty,
                "warehouse_name": first_stock.warehouse.name if first_stock and first_stock.warehouse else "",
                "is_low_stock": total_qty <= float(p.min_stock),
                "is_out_stock": total_qty <= 0,
            })
        context["inv_products"] = inv_products
        context["inv_warehouses"] = warehouses
        context["inv_total_warehouses"] = total_warehouses
        context["inv_total_stock_qty"] = float(total_stock_qty)
        context["inv_total_reserved"] = float(total_reserved)
        context["inv_available_stock"] = float(total_stock_qty - total_reserved)
        context["inv_low_stock_count"] = low_stock_count
        context["inv_out_stock_count"] = out_stock_count
        context["inv_low_stock_items"] = list(low_stock_items.values("id", "quantity", "product__name", "warehouse__name", "product__min_stock"))
        context["inv_recent_moves"] = recent_moves
        context["inv_products"] = inv_products
    if slug == "stock-movement":
        from apps.inventory.models import Warehouse, StockMovement
        context["sm_warehouses"] = list(Warehouse.objects.filter(is_active=True).values("id", "name"))
        context["sm_products"] = list(Product.objects.filter(is_active=True).values("id", "name", "sku")[:200])
        context["sm_recent_moves"] = list(StockMovement.objects.select_related("product", "warehouse").order_by("-created_at")[:50].values(
            "id", "movement_type", "quantity", "reference", "note", "created_at",
            product_name=F("product__name"), warehouse_name=F("warehouse__name")
        ))
    if slug == "warehouse-management":
        from apps.inventory.models import Warehouse, Stock
        whs = Warehouse.objects.filter(is_active=True)
        wh_list = []
        for w in whs:
            stocks = Stock.objects.filter(warehouse=w).select_related("product")
            sku_count = stocks.values("product").distinct().count()
            total_val = sum(float(s.quantity) * float(s.product.cost_price or 0) for s in stocks)
            total_qty = sum(float(s.quantity) for s in stocks)
        wh_list.append({
            "id": w.id, "name": w.name, "address": w.address or "",
            "manager": w.manager or "",
            "sku_count": sku_count, "total_value": round(total_val, 0),
            "total_qty": round(total_qty, 0),
            "capacity_pct": min(100, int((total_qty / 5000) * 100)) if total_qty else 0,
        })
        context["wh_warehouses"] = wh_list
        context["wh_total_value"] = round(sum(w["total_value"] for w in wh_list), 0)
    if slug == "stock-movement":
        from apps.inventory.models import Warehouse, StockMovement, Stock
        context["sm_warehouses"] = list(Warehouse.objects.filter(is_active=True).values("id", "name"))
        context["sm_products"] = list(Product.objects.filter(is_active=True).values("id", "name", "sku")[:200])
        sm_stock_by_wh = {}
        for w in Warehouse.objects.filter(is_active=True):
            total = Stock.objects.filter(warehouse=w).aggregate(t=Sum("quantity"))["t"] or 0
            sm_stock_by_wh[w.id] = {"name": w.name, "qty": float(total)}
        context["sm_stock_by_wh"] = sm_stock_by_wh
        context["sm_recent_moves"] = list(StockMovement.objects.select_related("product", "warehouse").order_by("-created_at")[:50].values(
            "id", "movement_type", "quantity", "reference", "note", "created_at",
            product_name=F("product__name"), warehouse_name=F("warehouse__name")
        ))
    if slug == "purchase-management":
        from apps.purchases.models import PurchaseOrder, Supplier, PurchaseItem, PurchaseReceipt
        from apps.inventory.models import Warehouse
        po_qs = PurchaseOrder.objects.select_related("supplier", "warehouse").order_by("-created_at")
        total_monthly = sum(float(o.total) for o in po_qs if o.order_date and o.order_date.month == timezone.now().month and o.order_date.year == timezone.now().year)
        open_orders = po_qs.exclude(status__in=["received", "cancelled"])
        open_count = open_orders.count()
        open_value = sum(float(o.total) for o in open_orders)
        pending_receipts = PurchaseReceipt.objects.count()
        supplier_debt = sum(float(o.total) for o in po_qs if o.status != "received")
        pm_orders = []
        for o in po_qs[:50]:
            status_label = o.status
            pm_orders.append({
                "id": o.id,
                "po_number": f"PO-{o.order_date.year if o.order_date else 1403}-{o.id:04d}",
                "supplier_name": o.supplier.company_name if o.supplier else "",
                "warehouse_name": o.warehouse.name if o.warehouse else "",
                "order_date": o.order_date.strftime("%Y/%m/%d") if o.order_date else "",
                "due_date": o.due_date.strftime("%Y/%m/%d") if o.due_date else "",
                "total": float(o.total),
                "status": o.status,
                "status_label": status_label,
                "finance_status": "tsv" if o.status == "received" else "pending",
            })
        context["pm_monthly_purchases"] = total_monthly
        context["pm_open_orders_count"] = open_count
        context["pm_open_orders_value"] = open_value
        context["pm_pending_receipts"] = pending_receipts
        context["pm_supplier_debt"] = supplier_debt
        context["pm_orders"] = pm_orders
        context["pm_suppliers"] = list(Supplier.objects.filter(is_active=True).values("id", "company_name"))
        context["pm_warehouses"] = list(Warehouse.objects.filter(is_active=True).values("id", "name"))
        context["pm_products"] = list(Product.objects.filter(is_active=True).values("id", "name", "sku")[:200])
    if slug == "supplier-management":
        from apps.purchases.models import Supplier, PurchaseOrder
        suppliers = Supplier.objects.filter(is_active=True)
        context["sm_suppliers"] = list(suppliers.values("id", "company_name", "contact_person", "phone", "email", "address"))
        context["sm_supplier_count"] = suppliers.count()
        context["sm_total_debt"] = sum(float(o.total) for o in PurchaseOrder.objects.filter(status__in=["pending", "approved"]))
        context["sm_monthly_purchases"] = sum(float(o.total) for o in PurchaseOrder.objects.filter(order_date__month=timezone.now().month, order_date__year=timezone.now().year))
        context["sm_open_orders"] = PurchaseOrder.objects.exclude(status__in=["received", "cancelled"]).count()
        context["sm_open_value"] = sum(float(o.total) for o in PurchaseOrder.objects.exclude(status__in=["received", "cancelled"]))
    if slug == "customer-management":
        from apps.customers.models import Customer
        from apps.sales.models import Invoice
        qs = Customer.objects.all()
        total = qs.count()
        active = qs.filter(is_active=True).count()
        debtors = qs.filter(credit_limit__gt=0).count()
        vip = qs.filter(loyalty_points__gte=1000).count()
        last30 = timezone.now() - timedelta(days=30)
        new_month = qs.filter(created_at__gte=last30).count()
        # Transaction volume from invoices
        total_volume = sum(float(inv.total) for inv in Invoice.objects.all())
        # Per-customer order count and debt
        customer_data = []
        for cust in qs.order_by("-created_at"):
            cust_invoices = Invoice.objects.filter(customer=cust)
            order_count = cust_invoices.count()
            total_debt = sum(float(inv.total) for inv in cust_invoices.filter(payment_status__in=["unpaid", "partial"]))
            customer_data.append({
                "id": cust.id, "name": cust.name, "phone": cust.phone, "email": cust.email,
                "address": cust.address, "credit_limit": float(cust.credit_limit),
                "loyalty_points": cust.loyalty_points, "is_active": cust.is_active,
                "created_at": cust.created_at, "order_count": order_count,
                "total_debt": total_debt, "total_volume": sum(float(inv.total) for inv in cust_invoices),
            })
        context["cm_total_customers"] = total
        context["cm_active_customers"] = active
        context["cm_debtor_customers"] = debtors
        context["cm_vip_customers"] = vip
        context["cm_new_month_customers"] = new_month
        context["cm_total_volume"] = total_volume
        context["cm_customers"] = customer_data
        context["customers"] = customer_data
    if slug == "dashboard":
        from apps.customers.models import Customer
        from apps.sales.models import Invoice, InvoiceItem
        from apps.inventory.models import Warehouse, Stock
        from apps.purchases.models import Supplier
        from apps.accounts.models import User
        context["products_count"] = Product.objects.count()
        context["customers_count"] = Customer.objects.count()
        context["invoices_count"] = Invoice.objects.count()
        context["total_sales"] = sum(i.total for i in Invoice.objects.all())
        context["warehouses_count"] = Warehouse.objects.count()
        context["suppliers_count"] = Supplier.objects.count()
        context["users_count"] = User.objects.count()
        context["low_stock_count"] = Stock.objects.filter(quantity__lte=0).count()
        context["recent_invoices"] = Invoice.objects.select_related("customer").order_by("-created_at")[:8]

        # Sales trend (last 30 days)
        today = timezone.now().date()
        start = today - timedelta(days=29)
        trend = (Invoice.objects.filter(invoice_date__gte=start)
                 .annotate(d=TruncDate('invoice_date'))
                 .values('d').annotate(total=Sum('total')).order_by('d'))
        trend_map = {t['d']: float(t['total'] or 0) for t in trend}
        labels = []
        values = []
        cur = start
        while cur <= today:
            labels.append(cur.strftime('%m/%d'))
            values.append(trend_map.get(cur, 0))
            cur += timedelta(days=1)
        context["sales_trend_labels"] = json.dumps(labels)
        context["sales_trend_values"] = json.dumps(values)

        # Top products by quantity
        top = (InvoiceItem.objects.values('product__name')
               .annotate(qty=Sum('quantity'))
               .order_by('-qty')[:5])
        context["top_products_labels"] = json.dumps([t['product__name'] for t in top])
        context["top_products_values"] = json.dumps([float(t['qty'] or 0) for t in top])

        # Low stock items
        context["low_stock_items"] = Stock.objects.filter(quantity__lte=F('product__min_stock')).select_related('product','warehouse')[:8]

        # Payment status
        context["paid_count"] = Invoice.objects.filter(payment_status='paid').count()
        context["unpaid_count"] = Invoice.objects.filter(payment_status='unpaid').count()
    if slug == "finance-center":
        from apps.finance.models import FinanceTransaction
        from apps.sales.models import Invoice
        from apps.purchases.models import PurchaseOrder
        context["fc_total_sales"] = sum(float(i.total) for i in Invoice.objects.all())
        context["fc_total_purchases"] = sum(float(o.total) for o in PurchaseOrder.objects.all())
        context["fc_transactions"] = list(FinanceTransaction.objects.order_by("-created_at")[:50].values("id", "tx_type", "amount", "note", "created_at"))
        context["fc_transaction_count"] = FinanceTransaction.objects.count()
    if slug == "global-search":
        from apps.customers.models import Customer
        from apps.purchases.models import Supplier
        context["gs_products"] = list(Product.objects.filter(is_active=True).values("id", "name", "sku", "barcode")[:50])
        context["gs_customers"] = list(Customer.objects.filter(is_active=True).values("id", "name", "phone")[:50])
        context["gs_suppliers"] = list(Supplier.objects.filter(is_active=True).values("id", "company_name")[:50])
    if slug == "cashbox-payments":
        from apps.customers.models import CustomerPayment
        context["cp_payments"] = list(CustomerPayment.objects.order_by("-created_at")[:50].values("id", "amount", "method", "reference", "note", "created_at", "customer__name"))
        context["cp_payment_count"] = CustomerPayment.objects.count()
        context["cp_total_payments"] = sum(float(p.amount) for p in CustomerPayment.objects.all())
    if slug == "sales-report":
        from apps.sales.models import Invoice, InvoiceItem, SalesReturn
        from decimal import Decimal
        invoices = Invoice.objects.all()
        total_sales = sum(float(i.total) for i in invoices)
        total_subtotal = sum(float(i.subtotal) for i in invoices)
        total_tax = sum(float(i.tax) for i in invoices)
        total_discount = sum(float(i.discount) for i in invoices)
        paid_invoices = invoices.filter(payment_status='paid')
        unpaid_invoices = invoices.filter(payment_status='unpaid')
        returns = SalesReturn.objects.all()
        total_returns = sum(float(r.total) for r in returns)
        net_sales = total_sales - total_returns
        context["sr_invoices"] = list(invoices.select_related("customer", "warehouse").order_by("-created_at")[:20].values(
            "id", "invoice_no", "customer__name", "customer__phone", "total", "status", "payment_status", "invoice_date"
        ))
        context["sr_invoice_count"] = invoices.count()
        context["sr_total_sales"] = total_sales
        context["sr_total_subtotal"] = total_subtotal
        context["sr_total_tax"] = total_tax
        context["sr_total_discount"] = total_discount
        context["sr_paid_count"] = paid_invoices.count()
        context["sr_unpaid_count"] = unpaid_invoices.count()
        context["sr_total_returns"] = total_returns
        context["sr_net_sales"] = net_sales
        context["sr_gross_profit"] = round(net_sales * 0.35, 2)
        # Category sales
        cat_sales = []
        cats = Category.objects.filter(is_active=True)
        for cat in cats:
            cat_items = InvoiceItem.objects.filter(product__category=cat).select_related("product")
            cat_total = sum(float(ii.unit_price * ii.quantity + ii.tax - ii.discount) for ii in cat_items) if cat_items else 0
            cat_profit = round(cat_total * 0.30, 2)
            cat_margin_pct = round((cat_profit / cat_total * 100) if cat_total > 0 else 0, 1)
            cat_sales.append({
                "name": cat.name,
                "sales": cat_total,
                "profit": cat_profit,
                "margin_pct": cat_margin_pct,
                "bg_pct": round(100 - cat_margin_pct, 1),
            })
        cat_sales.sort(key=lambda x: x["sales"], reverse=True)
        context["sr_cat_sales"] = cat_sales[:5]
    if slug == "sales-return":
        from apps.sales.models import SalesReturn
        context["sret_returns"] = list(SalesReturn.objects.select_related("invoice").order_by("-created_at")[:50].values("id", "invoice__invoice_no", "total", "reason", "created_at"))
        context["sret_return_count"] = SalesReturn.objects.count()
    if slug == "pricing-discounts":
        context["pd_products"] = list(Product.objects.filter(is_active=True).values("id", "name", "sku", "cost_price", "sale_price")[:50])
        context["pd_pricelists"] = list(PriceList.objects.all().values("id", "name", "price", "valid_from", "valid_to")[:20])
        context["pd_discounts"] = list(Discount.objects.all().values("id", "name", "discount_type", "value", "valid_from", "valid_to")[:20])
    if slug == "profit-loss-report":
        from apps.sales.models import Invoice
        from apps.purchases.models import PurchaseOrder
        context["plr_total_sales"] = sum(float(i.total) for i in Invoice.objects.all())
        context["plr_total_purchases"] = sum(float(o.total) for o in PurchaseOrder.objects.all())
        context["plr_profit"] = context["plr_total_sales"] - context["plr_total_purchases"]
    if slug == "cashbox-payments":
        from apps.finance.models import Cashbox
        context["cb_cashboxes"] = list(Cashbox.objects.filter(is_active=True).values("id", "name", "balance"))
        context["cb_cashbox_count"] = Cashbox.objects.filter(is_active=True).count()
        context["cb_total_balance"] = sum(float(c.balance) for c in Cashbox.objects.filter(is_active=True))
    if slug == "settings":
        from apps.settings_app.models import StoreSettings
        s = StoreSettings.objects.first()
        context["settings_store"] = s
        context["settings_store_name"] = s.store_name if s else "فروشگاه"
        context["settings_support_phone"] = s.support_phone if s else ""
        context["settings_currency"] = s.currency if s else "IRT"
        context["settings_branch_name"] = s.branch_name if s and hasattr(s, 'branch_name') else ""
    if slug == "user-management":
        from apps.accounts.models import User
        users = User.objects.all()
        context["um_users"] = list(users.values("id", "username", "first_name", "last_name", "email", "phone", "role", "branch", "is_active", "is_staff", "is_superuser", "date_joined", "last_login"))
        context["um_user_count"] = users.count()
        context["um_active_count"] = users.filter(is_active=True).count()
        context["um_staff_count"] = users.filter(is_staff=True).count()
    if slug == "pos":
        from apps.inventory.models import Warehouse, Stock
        from apps.customers.models import Customer
        from apps.settings_app.models import StoreSettings
        from apps.accounts.models import User
        # انبار پیش‌فرض: اولین انبار فعال (یا انتخاب ذخیره‌شدهٔ کاربر)
        warehouses = Warehouse.objects.filter(is_active=True).order_by("id")
        default_warehouse = warehouses.first()
        context["pos_warehouses"] = list(warehouses.values("id", "name"))
        context["pos_default_warehouse"] = default_warehouse.id if default_warehouse else None
        # دسته‌بندی‌ها با شمارش محصول فعال (+ آیکن/رنگ برای تب‌ها)
        CATEGORY_ICONS = {
            "نوشیدنی و قهوه": ("coffee", "text-amber-500"),
            "روغن و چاشنی": ("water_drop", "text-sky-400"),
            "بهداشتی و شوینده": ("sanitizer", "text-emerald-400"),
            "خشکبار و آجیل": ("grain", "text-amber-400"),
            "شیرینی و عسل": ("bakery_dining", "text-blue-400"),
            "مواد غذایی": ("restaurant", "text-orange-400"),
            "لبنیات": ("local_drink", "text-blue-300"),
        }
        cats = (Category.objects.filter(is_active=True, parent__isnull=True)
                .annotate(n=Count("product", filter=Q(product__is_active=True))))
        pos_categories = []
        for c in cats:
            icon, color = CATEGORY_ICONS.get(c.name, ("category", "text-slate-400"))
            pos_categories.append((c.name, icon, color, c.n))
        context["pos_categories"] = pos_categories
        context["pos_total_products"] = Product.objects.filter(is_active=True).count()
        # محصولات فعال + موجودی انبار پیش‌فرض
        stock_map = {}
        if default_warehouse:
            for s in Stock.objects.filter(warehouse=default_warehouse).select_related("product"):
                stock_map[s.product_id] = float(s.quantity)
        prods = (Product.objects.filter(is_active=True)
                 .select_related("category", "brand")
                 .order_by("id"))
        pos_products = []
        for p in prods:
            stock_qty = stock_map.get(p.id, 0)
            min_stock = float(p.min_stock or 0)
            if stock_qty <= 0:
                stock_state = "out"
            elif min_stock > 0 and stock_qty <= min_stock:
                stock_state = "low"
            else:
                stock_state = "ok"
            pos_products.append({
                "id": p.id, "name": p.name, "barcode": p.barcode or p.sku,
                "price": float(p.sale_price or 0),
                "description": p.description or "",
                "image_url": p.image.url if p.image else None,
                "category": p.category.name if p.category else "",
                "stock_qty": stock_qty, "stock_state": stock_state,
            })
        context["pos_products"] = pos_products
        # مشتریان برای انتخابگر
        context["pos_customers"] = list(Customer.objects.filter(is_active=True).values("id", "name", "phone")[:100])
        # موجودی همهٔ انبارها برای تعویض زنده در POS
        _stock_by_wh = {}
        for _s in Stock.objects.select_related("product", "warehouse").all():
            _stock_by_wh.setdefault(_s.product_id, {})[_s.warehouse_id] = float(_s.quantity or 0) - float(_s.reserved or 0)
        context["pos_stock_by_warehouse"] = {str(pid): {str(wid): qty for wid, qty in whs.items()} for pid, whs in _stock_by_wh.items()}
        # اطلاعات فروشگاه/کاربر برای چاپ
        s = StoreSettings.objects.first()
        context["pos_store"] = {
            "store_name": (s.store_name if s and s.store_name else "فروشگاه"),
            "support_phone": (s.support_phone if s else ""),
            "currency": (s.currency if s else "IRT"),
        }
        u = request.user
        if u.is_authenticated:
            context["pos_cashier"] = (u.get_full_name() or u.username)
        else:
            context["pos_cashier"] = ""
    return render(request, tpl, context)
