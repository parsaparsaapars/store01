from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import Notification
from .serializers import NotificationSerializer

def index(request):
    return HttpResponse("notifications app ok")

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all(); serializer_class = NotificationSerializer; permission_classes=[permissions.IsAuthenticated]
