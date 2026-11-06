from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("ui/<slug:slug>/", views.page, name="page"),
    path("api/status/", views.system_status, name="system_status"),
]
