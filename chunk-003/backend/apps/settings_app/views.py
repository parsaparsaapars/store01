from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import StoreSettings
from .serializers import StoreSettingsSerializer

def index(request):
    return HttpResponse("settings app ok")

class StoreSettingsViewSet(viewsets.ModelViewSet):
    queryset = StoreSettings.objects.all(); serializer_class = StoreSettingsSerializer; permission_classes=[permissions.IsAuthenticated]
