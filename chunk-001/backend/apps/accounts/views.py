from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    u = request.user
    name = (u.get_full_name() or u.username).strip()
    return JsonResponse({"id": u.id, "username": u.username, "name": name})

@api_view(["POST"])
@permission_classes([])
def password_reset_request(request):
    """درخواست بازیابی رمز: ثبت اعلان critical برای مدیران + رکورد درخواست."""
    import secrets
    username = (request.data.get("username") or "").strip()
    if not username:
        return JsonResponse({"ok": False, "message": "نام کاربری را وارد کنید."}, status=400)
    User = get_user_model()
    user = User.objects.filter(username=username).first()
    ticket = "RST-" + secrets.token_hex(4).upper()
    # ثبت اعلان برای همهٔ مدیران
    try:
        from apps.notifications.models import Notification
        Notification.objects.create(
            title="درخواست بازیابی رمز عبور",
            message=(f"کاربر «{username}» درخواست بازیابی رمز داده است. "
                     f"کد پیگیری: {ticket} — لطفاً برای تأیید هویت و تعیین رمز جدید اقدام کنید."),
            category="امنیت",
            priority="critical",
            link="/ui/user-management/",
        )
    except Exception:
        pass
    # حتی اگر کاربر وجود نداشت هم پیام یکسان برمی‌گردد (user enumeration نشود)
    return JsonResponse({
        "ok": True,
        "ticket": ticket,
        "message": "درخواست شما ثبت شد. کارشناس پشتیبانی پس از تأیید هویت با شما تماس می‌گیرد.",
    })
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from .models import User, Role, AuditLog
from .serializers import UserSerializer, RoleSerializer, AuditLogSerializer

def index(request):
    return HttpResponse("accounts app ok")

def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:page", slug="pos")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me") == "on"
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # مرا به خاطر بسپار: سشن دائمی (۳۰ روز) یا تا بستن مرورگر
                request.session.set_expiry(30 * 24 * 60 * 60 if remember_me else 0)
                return redirect("core:page", slug="pos")
            messages.error(request, "حساب کاربری شما غیرفعال است.")
        else:
            # check if user exists but wrong password
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                messages.error(request, "رمز عبور اشتباه است.")
            else:
                messages.error(request, "نام کاربری یافت نشد.")
    return render(request, "ui/login/code.html", _login_context())

def _login_context():
    """مقادیر نمایشی صفحهٔ لاگین (شعبه/پشتیبانی/نسخه) از تنظیمات فروشگاه."""
    ctx = {
        "branch_name": "شعبه مرکزی - صندوق ۱",
        "support_phone": "۰۲۱-۸۸۹۹۰۰۰۰",
        "system_version": "۴.۸.۲ سازمانی",
    }
    try:
        from apps.settings_app.models import StoreSettings
        s = StoreSettings.objects.first()
        if s:
            ctx["branch_name"] = s.branch_name or ctx["branch_name"]
            ctx["support_phone"] = s.support_phone or ctx["support_phone"]
            ctx["system_version"] = s.system_version or ctx["system_version"]
    except Exception:
        pass
    return ctx

def logout_view(request):
    logout(request)
    return redirect("accounts:login")

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all(); serializer_class = RoleSerializer; permission_classes=[permissions.IsAuthenticated]
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all(); serializer_class = UserSerializer; permission_classes=[permissions.IsAuthenticated]
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all(); serializer_class = AuditLogSerializer; permission_classes=[permissions.IsAuthenticated]
