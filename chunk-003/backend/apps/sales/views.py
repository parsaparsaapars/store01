from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction as db_transaction
from django.utils import timezone
from .models import Invoice, InvoiceItem, InvoicePayment, SalesReturn, SalesReturnItem
from .serializers import InvoiceSerializer, InvoiceItemSerializer, InvoicePaymentSerializer, SalesReturnSerializer, SalesReturnItemSerializer

def index(request):
    return HttpResponse("sales app ok")

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def pos_checkout(request):
    """ثبت فروش کامل POS: فاکتور + اقلام + پرداخت + کسر موجودی — همه در یک تراکنش DB."""
    data = request.data
    items = data.get("items") or []
    if not items:
        return JsonResponse({"ok": False, "message": "سبد خرید خالی است."}, status=400)
    warehouse_id = data.get("warehouse")
    from apps.inventory.models import Warehouse
    warehouse = Warehouse.objects.filter(id=warehouse_id).first()
    if not warehouse:
        warehouse = Warehouse.objects.filter(is_active=True).order_by("id").first()
    if not warehouse:
        return JsonResponse({"ok": False, "message": "انباری یافت نشد."}, status=400)

    # اقلام: اعتبارسنجی محصول
    from apps.products.models import Product
    lines = []
    for it in items:
        pid = it.get("product")
        p = Product.objects.filter(id=pid).first()
        if not p:
            return JsonResponse({"ok": False, "message": f"محصول با شناسه {pid} یافت نشد."}, status=400)
        try:
            qty = float(it.get("quantity") or 0)
            unit_price = float(it.get("unit_price") or 0)
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "message": "تعداد یا قیمت نامعتبر است."}, status=400)
        if qty <= 0:
            return JsonResponse({"ok": False, "message": f"تعداد «{p.name}» باید مثبت باشد."}, status=400)
        lines.append({"product": p, "qty": qty, "unit_price": unit_price,
                      "discount": float(it.get("discount") or 0), "tax": float(it.get("tax") or 0)})

    subtotal = sum(l["unit_price"] * l["qty"] for l in lines)

    # تخفیف و مالیات (مقدار یا درصد)
    def _apply(mode, inp, base):
        try:
            inp = float(inp or 0)
        except (TypeError, ValueError):
            inp = 0
        if mode == "percent":
            return round(base * inp / 100)
        return round(inp)
    discount = _apply(data.get("discount_mode", "amount"), data.get("discount_input"), subtotal)
    discount = max(0, min(discount, subtotal))
    base_after_discount = subtotal - discount
    tax = _apply(data.get("tax_mode", "amount"), data.get("tax_input"), base_after_discount)
    tax = max(0, tax)
    shipping = float(data.get("shipping") or 0)
    total = subtotal - discount + tax + shipping

    # شماره فاکتور یکتا
    from apps.settings_app.models import StoreSettings
    prefix = "INV"
    try:
        s = StoreSettings.objects.first()
        if s and s.invoice_prefix:
            prefix = s.invoice_prefix
    except Exception:
        pass
    invoice_no = data.get("invoice_no")
    if not invoice_no:
        invoice_no = f"{prefix}-{int(timezone.now().timestamp() * 1000)}"
    if Invoice.objects.filter(invoice_no=invoice_no).exists():
        invoice_no = f"{invoice_no}-{timezone.now().strftime('%H%M%S')}"

    # مشتری اختیاری
    customer = None
    cid = data.get("customer")
    if cid:
        from apps.customers.models import Customer
        customer = Customer.objects.filter(id=cid).first()

    payment_method = data.get("method") or "cash"
    note = data.get("note") or ""

    # اعتبارسنجی موجودی قبل از ثبت (فروش بیش از موجودی ممنوع)
    from apps.inventory.models import Stock
    for l in lines:
        stock = Stock.objects.filter(product=l["product"], warehouse=warehouse).first()
        available = float(stock.quantity) if stock else 0.0
        if l["qty"] > available:
            return JsonResponse({
                "ok": False,
                "message": f"موجودی «{l['product'].name}» کافی نیست (موجودی: {available:g}).",
            }, status=400)

    try:
        with db_transaction.atomic():
            invoice = Invoice.objects.create(
                invoice_no=invoice_no,
                customer=customer,
                invoice_date=timezone.now().date(),
                warehouse=warehouse,
                status="final",
                payment_status="paid" if data.get("paid", True) else "unpaid",
                subtotal=subtotal, discount=discount,
                discount_mode=data.get("discount_mode", "amount"),
                discount_input=float(data.get("discount_input") or 0),
                tax=tax,
                tax_mode=data.get("tax_mode", "amount"),
                tax_input=float(data.get("tax_input") or 0),
                shipping=shipping, total=total, note=note,
                created_by=request.user if request.user.is_authenticated else None,
            )
            for l in lines:
                InvoiceItem.objects.create(
                    invoice=invoice, product=l["product"],
                    quantity=l["qty"], unit_price=l["unit_price"],
                    discount=l["discount"], tax=l["tax"],
                )
            InvoicePayment.objects.create(
                invoice=invoice, amount=total, method=payment_method,
                reference=data.get("reference") or "",
            )
            # کسر موجودی انبار + ثبت گردش
            from apps.inventory.models import Stock, StockMovement
            from decimal import Decimal
            for l in lines:
                stock, _ = Stock.objects.get_or_create(product=l["product"], warehouse=warehouse)
                stock.quantity -= Decimal(str(l["qty"]))
                stock.save()
                StockMovement.objects.create(
                    product=l["product"], warehouse=warehouse,
                    movement_type="out", quantity=Decimal(str(l["qty"])),
                    reference=invoice_no, note="فروش POS",
                    created_by=request.user if request.user.is_authenticated else None,
                )
    except Exception as e:
        return JsonResponse({"ok": False, "message": f"خطا در ثبت فاکتور: {e}"}, status=500)

    return JsonResponse({
        "ok": True,
        "invoice_id": invoice.id,
        "invoice_no": invoice.invoice_no,
        "total": float(invoice.total),
        "payment_status": invoice.payment_status,
        "message": f"فاکتور {invoice.invoice_no} با موفقیت ثبت شد.",
    })

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all(); serializer_class = InvoiceSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all(); serializer_class = InvoiceItemSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class InvoicePaymentViewSet(viewsets.ModelViewSet):
    queryset = InvoicePayment.objects.all(); serializer_class = InvoicePaymentSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class SalesReturnViewSet(viewsets.ModelViewSet):
    queryset = SalesReturn.objects.all(); serializer_class = SalesReturnSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class SalesReturnItemViewSet(viewsets.ModelViewSet):
    queryset = SalesReturnItem.objects.all(); serializer_class = SalesReturnItemSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
